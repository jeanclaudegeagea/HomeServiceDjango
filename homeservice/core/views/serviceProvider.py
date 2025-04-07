from ..models import User, Customer, ServiceProvider, Service, Booking, ServiceReview
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Count
import json


def service_provider_profile(request, id):
    # Retrieve the service provider related to the given user_id
    service_provider = ServiceProvider.objects.get(user_id=id)

    # Get the years_of_experience and specializations
    years_of_experience = service_provider.years_of_experience
    specializations = service_provider.specialization.all()

    # Get the services provided by this service provider that are active
    services = (
        Service.objects.filter(provider=service_provider, is_active=True)
        .select_related("provider__user", "specialization")
        .order_by("-created_at")
    )

    # Get review stats
    review_stats = service_provider.reviews_received.aggregate(
        average_rating=Avg("rating"), review_count=Count("id")
    )

    average_rating = review_stats["average_rating"] or 0  # Default to 0 if no reviews
    review_count = review_stats["review_count"]

    context = {
        "service_provider": service_provider,
        "years_of_experience": years_of_experience,
        "specializations": specializations,
        "services": services,
        "average_rating": round(average_rating, 1),
        "review_count": review_count,
    }

    if hasattr(request.user, "role"):
        if request.user.role == User.CUSTOMER:
            customer = Customer.objects.get(user=request.user)
            customer_bookings = Booking.objects.filter(customer=customer)
            context["customer_bookings"] = customer_bookings

    if request.user.is_authenticated:
        if request.user.role == User.CUSTOMER:
            customer = Customer.objects.get(user=request.user)
            customer_bookings = Booking.objects.filter(customer=customer)
            context["customer_bookings"] = customer_bookings

            # ✅ Get the customer's review (if it exists)
            try:
                existing_review = ServiceReview.objects.get(
                    customer=customer, provider=service_provider
                )
                context["customer_review_rating"] = existing_review.rating
                context["customer_review_content"] = existing_review.content
            except ServiceReview.DoesNotExist:
                context["customer_review_rating"] = 1
                context["customer_review_content"] = ""

    return render(request, "core/service_provider_profile.html", context)


@csrf_exempt
@login_required
def add_review(request, customer_id, service_provider_id):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Invalid request method."}, status=405
        )

    try:
        data = json.loads(request.body)
        rating = data.get("rating")
        review_content = data.get("customer_review")

        if not rating or not review_content.strip():
            return JsonResponse(
                {"success": False, "error": "Rating and review content are required."},
            )

        try:
            customer = Customer.objects.get(pk=customer_id)
            provider = ServiceProvider.objects.get(pk=service_provider_id)
        except Customer.DoesNotExist:
            return JsonResponse({"success": False, "error": "Customer not found."})
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Service provider not found."}
            )

        # Ensure customer matches the logged-in user
        if customer.user != request.user:
            return JsonResponse({"success": False, "error": "Unauthorized action."})

        review, created = ServiceReview.objects.update_or_create(
            customer=customer,
            provider=provider,
            defaults={
                "rating": rating,
                "content": review_content,
            },
        )

        if created:
            message = "Review submitted successfully!"
        else:
            message = "Review updated successfully!"
        return JsonResponse({"success": True, "message": message})

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON data."}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
