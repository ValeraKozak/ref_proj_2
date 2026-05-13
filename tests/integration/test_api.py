from src.models.entities import Listing, ListingStatus, Role
from tests.conftest import auth_header


def test_healthcheck(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login_flow(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "api@example.com",
            "full_name": "Api User",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "api@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_listing_moderation_and_message_flow(client, db_session, seeded_users, seeded_category):
    seeded_users["moderator"].role = Role.MODERATOR
    db_session.commit()

    create_response = client.post(
        "/listings",
        json={
            "title": "MacBook Air M2",
            "description": "Great notebook for work and study with charger and warranty included.",
            "price": 950,
            "category_id": seeded_category.id,
            "image_urls": ["https://images.example.com/macbook-air-m2.jpg"],
        },
        headers=auth_header(seeded_users["owner"].email),
    )
    assert create_response.status_code == 201
    assert create_response.json()["image_urls"] == ["https://images.example.com/macbook-air-m2.jpg"]
    listing_id = create_response.json()["id"]

    moderation_response = client.post(
        f"/moderation/listings/{listing_id}",
        json={"approved": True},
        headers=auth_header(seeded_users["moderator"].email),
    )
    assert moderation_response.status_code == 200

    public_response = client.get("/listings")
    assert public_response.status_code == 200
    assert len(public_response.json()) == 1

    message_response = client.post(
        "/messages",
        json={
            "listing_id": listing_id,
            "recipient_id": seeded_users["owner"].id,
            "body": "Is the laptop still available?",
        },
        headers=auth_header(seeded_users["buyer"].email),
    )
    assert message_response.status_code == 201


def test_blocked_user_cannot_create_listing(client, db_session, seeded_users, seeded_category):
    seeded_users["owner"].is_blocked = True
    db_session.commit()

    response = client.post(
        "/listings",
        json={
            "title": "Blocked listing",
            "description": "This description is long enough for request validation to pass.",
            "price": 100,
            "category_id": seeded_category.id,
        },
        headers=auth_header(seeded_users["owner"].email),
    )
    assert response.status_code == 403


def test_non_moderator_cannot_review_listing(client, seeded_users, approved_listing):
    response = client.post(
        f"/moderation/listings/{approved_listing.id}",
        json={"approved": True},
        headers=auth_header(seeded_users["buyer"].email),
    )
    assert response.status_code == 403


def test_category_crud_flow_for_admin(client, seeded_users):
    create_response = client.post(
        "/categories",
        json={"name": "Services", "description": "Freelance and local services"},
        headers=auth_header(seeded_users["admin"].email),
    )
    assert create_response.status_code == 201
    category_id = create_response.json()["id"]

    get_response = client.get(f"/categories/{category_id}")
    assert get_response.status_code == 200

    update_response = client.put(
        f"/categories/{category_id}",
        json={"name": "Business Services", "description": "Updated description"},
        headers=auth_header(seeded_users["admin"].email),
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Business Services"

    delete_response = client.delete(
        f"/categories/{category_id}",
        headers=auth_header(seeded_users["admin"].email),
    )
    assert delete_response.status_code == 200


def test_listing_detail_owned_list_and_archive_flow(
    client,
    db_session,
    seeded_users,
    seeded_category,
):
    create_response = client.post(
        "/listings",
        json={
            "title": "Sony Playstation 5",
            "description": "Console in excellent condition with two controllers and warranty.",
            "price": 500,
            "category_id": seeded_category.id,
            "image_urls": ["https://images.example.com/ps5.jpg"],
        },
        headers=auth_header(seeded_users["owner"].email),
    )
    assert create_response.status_code == 201
    listing_id = create_response.json()["id"]

    my_response = client.get("/listings/me/owned", headers=auth_header(seeded_users["owner"].email))
    assert my_response.status_code == 200
    assert len(my_response.json()) == 1

    detail_response = client.get(
        f"/listings/{listing_id}",
        headers=auth_header(seeded_users["owner"].email),
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["image_urls"] == ["https://images.example.com/ps5.jpg"]

    delete_response = client.delete(
        f"/listings/{listing_id}",
        headers=auth_header(seeded_users["owner"].email),
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Listing deleted"


def test_users_admin_and_profile_endpoints(client, seeded_users):
    me_response = client.get("/users/me", headers=auth_header(seeded_users["owner"].email))
    assert me_response.status_code == 200

    update_me_response = client.patch(
        "/users/me",
        json={"full_name": "Owner Updated"},
        headers=auth_header(seeded_users["owner"].email),
    )
    assert update_me_response.status_code == 200
    assert update_me_response.json()["full_name"] == "Owner Updated"

    list_users_response = client.get("/users", headers=auth_header(seeded_users["admin"].email))
    assert list_users_response.status_code == 200
    assert len(list_users_response.json()) == 4

    admin_patch_response = client.patch(
        f"/users/{seeded_users['buyer'].id}",
        json={"role": "moderator", "is_blocked": True},
        headers=auth_header(seeded_users["admin"].email),
    )
    assert admin_patch_response.status_code == 200
    assert admin_patch_response.json()["role"] == "moderator"
    assert admin_patch_response.json()["is_blocked"] is True


def test_message_read_and_delete_flow(client, db_session, seeded_users, seeded_category):
    create_response = client.post(
        "/listings",
        json={
            "title": "Canon Camera",
            "description": "Camera with lens, bag and charger in very good condition.",
            "price": 350,
            "category_id": seeded_category.id,
        },
        headers=auth_header(seeded_users["owner"].email),
    )
    listing_id = create_response.json()["id"]
    moderation_response = client.post(
        f"/moderation/listings/{listing_id}",
        json={"approved": True},
        headers=auth_header(seeded_users["moderator"].email),
    )
    assert moderation_response.status_code == 200

    message_response = client.post(
        "/messages",
        json={
            "listing_id": listing_id,
            "recipient_id": seeded_users["owner"].id,
            "body": "Can you share more photos?",
        },
        headers=auth_header(seeded_users["buyer"].email),
    )
    assert message_response.status_code == 201
    message_id = message_response.json()["id"]

    get_response = client.get(
        f"/messages/{message_id}",
        headers=auth_header(seeded_users["buyer"].email),
    )
    assert get_response.status_code == 200

    delete_response = client.delete(
        f"/messages/{message_id}",
        headers=auth_header(seeded_users["buyer"].email),
    )
    assert delete_response.status_code == 200


def test_public_listing_filters_and_sorting(client, db_session, seeded_users, seeded_category):
    first_listing = client.post(
        "/listings",
        json={
            "title": "Vintage Camera",
            "description": "Analog camera with leather case and a fully working shutter mechanism.",
            "price": 180,
            "category_id": seeded_category.id,
            "image_urls": ["https://images.example.com/vintage-camera.jpg"],
        },
        headers=auth_header(seeded_users["owner"].email),
    )
    second_listing = client.post(
        "/listings",
        json={
            "title": "Modern Mirrorless Camera",
            "description": "Mirrorless camera with kit lens, charger, battery grip and camera bag.",
            "price": 860,
            "category_id": seeded_category.id,
            "image_urls": ["https://images.example.com/mirrorless-camera.jpg"],
        },
        headers=auth_header(seeded_users["owner"].email),
    )

    first = db_session.get(Listing, first_listing.json()["id"])
    second = db_session.get(Listing, second_listing.json()["id"])
    assert first is not None
    assert second is not None
    first.status = ListingStatus.APPROVED
    second.status = ListingStatus.APPROVED
    db_session.commit()

    response = client.get(
        "/listings",
        params={
            "query": "camera",
            "min_price": 200,
            "sort_by": "price",
            "sort_order": "desc",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Modern Mirrorless Camera"


def test_image_upload_accepts_valid_png_signature(client, seeded_users):
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
    )
    response = client.post(
        "/uploads/images",
        files={"files": ("pixel.png", png_bytes, "image/png")},
        headers=auth_header(seeded_users["owner"].email),
    )

    assert response.status_code == 201
    assert response.json()["files"][0]["url"].endswith(".png")


def test_image_upload_rejects_spoofed_content_type(client, seeded_users):
    response = client.post(
        "/uploads/images",
        files={"files": ("fake.png", b"not really an image", "image/png")},
        headers=auth_header(seeded_users["owner"].email),
    )

    assert response.status_code == 400
    assert "does not match the declared image type" in response.json()["detail"]
