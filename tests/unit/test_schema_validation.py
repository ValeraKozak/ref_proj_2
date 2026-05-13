import pytest
from pydantic import ValidationError

from src.dto.schemas import (
    CategoryCreateDTO,
    CategoryUpdateDTO,
    ListingCreateDTO,
    ListingUpdateDTO,
    MessageCreateDTO,
    ModerationDecisionDTO,
    UploadImageBatchDTO,
    UserAdminUpdateDTO,
    UserCreateDTO,
    UserLoginDTO,
    UserUpdateDTO,
)
from src.models.entities import Role


@pytest.mark.parametrize(
    ("email", "full_name", "password"),
    [
        ("user1@example.com", "User One", "password123"),
        ("user2@example.com", "User Two", "Password123"),
        ("user3@example.com", "Valid User", "secretpass1"),
        ("user4@example.com", "A B", "abcdefgh"),
        ("user5@example.com", "Long Valid Name", "12345678"),
        ("user6@example.com", "User Six", "qwertyui"),
        ("user7@example.com", "Марко", "password9"),
        ("user8@example.com", "Seller Demo", "passpass"),
        ("user9@example.com", "Buyer Demo", "zxcasdqwe"),
        ("user10@example.com", "Moderator Demo", "moderator1"),
        ("user11@example.com", "Admin Demo", "adminpass8"),
        ("user12@example.com", "User Twelve", "valid-pass-1"),
    ],
)
def test_user_create_dto_accepts_valid_inputs(email, full_name, password):
    dto = UserCreateDTO(email=email, full_name=full_name, password=password)
    assert dto.email == email
    assert dto.full_name == full_name


@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        ({"email": "bad-email", "full_name": "User", "password": "password123"}, "email"),
        ({"email": "user@example.com", "full_name": "U", "password": "password123"}, "full_name"),
        ({"email": "user@example.com", "full_name": "", "password": "password123"}, "full_name"),
        ({"email": "user@example.com", "full_name": "User", "password": "short"}, "password"),
        ({"email": "", "full_name": "User", "password": "password123"}, "email"),
        ({"email": "test@localhost", "full_name": "User", "password": "password123"}, "email"),
        ({"email": "user@", "full_name": "User", "password": "password123"}, "email"),
        ({"email": "user@example.com", "full_name": "X", "password": "12345678"}, "full_name"),
        ({"email": "user@example.com", "full_name": "User", "password": ""}, "password"),
        ({"email": "user example.com", "full_name": "User", "password": "password123"}, "email"),
        ({"email": "user@example.com", "full_name": "User", "password": "1234567"}, "password"),
    ],
)
def test_user_create_dto_rejects_invalid_inputs(payload, expected_field):
    with pytest.raises(ValidationError) as exc_info:
        UserCreateDTO(**payload)
    assert expected_field in str(exc_info.value)


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("login1@example.com", "password123"),
        ("login2@example.com", "Password123"),
        ("seller@example.com", "Admin123!"),
        ("buyer@example.com", "Admin123!"),
        ("moderator@example.com", "Admin123!"),
        ("admin@example.com", "Admin123!"),
        ("user+tag@example.com", "long-enough-password"),
        ("first.last@example.com", "pa55word!"),
    ],
)
def test_user_login_dto_accepts_valid_inputs(email, password):
    dto = UserLoginDTO(email=email, password=password)
    assert dto.email == email
    assert dto.password == password


@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        ({"email": "bad", "password": "password123"}, "email"),
        ({"email": "", "password": "password123"}, "email"),
        ({"email": "user@", "password": "password123"}, "email"),
        ({"email": "not-an-email", "password": "pass"}, "email"),
        ({"email": "test@localhost", "password": "password123"}, "email"),
        ({"email": "user example.com", "password": "password123"}, "email"),
        ({"email": "@example.com", "password": "password123"}, "email"),
    ],
)
def test_user_login_dto_rejects_invalid_email_inputs(payload, expected_field):
    with pytest.raises(ValidationError) as exc_info:
        UserLoginDTO(**payload)
    assert expected_field in str(exc_info.value)


@pytest.mark.parametrize(
    ("name", "description"),
    [
        ("Electronics", "Phones, tablets and laptops"),
        ("Vehicles", "Cars, bikes and transport"),
        ("Services", "Professional and local services"),
        ("Pets", "Pet accessories and services"),
        ("Jobs", "Jobs and freelance offers"),
        ("Fashion", "Clothes, shoes and accessories"),
        ("Garden", "Garden tools and outdoor items"),
        ("Books", "Books and educational items"),
        ("Kids", "Children products and toys"),
        ("Real Estate", "Apartments, houses and rooms"),
        ("Office", "Office supplies and furniture"),
        ("Sports", "Sports gear and accessories"),
    ],
)
def test_category_create_dto_accepts_valid_inputs(name, description):
    dto = CategoryCreateDTO(name=name, description=description)
    assert dto.name == name


@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        ({"name": "A", "description": "Valid description"}, "name"),
        ({"name": "", "description": "Valid description"}, "name"),
        ({"name": "Valid", "description": "1234"}, "description"),
        ({"name": "Valid", "description": ""}, "description"),
        ({"name": "X", "description": "tiny"}, "name"),
        ({"name": "Valid", "description": "abcd"}, "description"),
        ({"name": "B", "description": "Long enough"}, "name"),
        ({"name": "", "description": "abcd"}, "name"),
        ({"name": "Valid", "description": "shrt"}, "description"),
    ],
)
def test_category_create_dto_rejects_invalid_inputs(payload, expected_field):
    with pytest.raises(ValidationError) as exc_info:
        CategoryCreateDTO(**payload)
    assert expected_field in str(exc_info.value)


@pytest.mark.parametrize(
    ("name", "description"),
    [
        ("Electronics", "Updated description one"),
        ("Vehicles", "Updated description two"),
        ("Services", "Updated description three"),
        ("Pets", "Updated description four"),
        ("Jobs", "Updated description five"),
        ("Fashion", "Updated description six"),
        ("Garden", "Updated description seven"),
        ("Books", "Updated description eight"),
    ],
)
def test_category_update_dto_accepts_valid_inputs(name, description):
    dto = CategoryUpdateDTO(name=name, description=description)
    assert dto.description == description


@pytest.mark.parametrize(
    ("title", "price", "category_id"),
    [
        ("Apple iPhone 14", 100.0, 1),
        ("Samsung Galaxy S23", 200.5, 2),
        ("Office Chair Pro", 49.99, 3),
        ("Mountain Bike 26", 310.0, 4),
        ("Winter Boots Men", 80.0, 5),
        ("Vintage Camera Kit", 155.75, 6),
        ("Math Tutoring Session", 25.0, 7),
        ("Sony Headphones XM5", 215.0, 8),
        ("Kids Wooden Toy Set", 34.0, 9),
        ("Garden Hose Premium", 22.0, 10),
        ("Robot Vacuum Cleaner", 280.0, 11),
        ("Studio Apartment Offer", 450.0, 12),
        ("Road Bike Helmet Giro", 32.0, 13),
        ("Acoustic Guitar Yamaha", 135.0, 14),
        ("Nintendo Switch OLED", 310.0, 15),
    ],
)
def test_listing_create_dto_accepts_valid_inputs(title, price, category_id):
    dto = ListingCreateDTO(
        title=title,
        description="This is a sufficiently long description for a listing validation case.",
        price=price,
        category_id=category_id,
        image_urls=["https://images.example.com/item.jpg"],
    )
    assert dto.title == title
    assert dto.price == price
    assert dto.image_urls


@pytest.mark.parametrize(
    ("title", "expected_title"),
    [
        ("  Trimmed Title 1  ", "Trimmed Title 1"),
        ("  Trimmed Title 2", "Trimmed Title 2"),
        ("Trimmed Title 3  ", "Trimmed Title 3"),
        ("  Office Desk Offer ", "Office Desk Offer"),
        ("  MacBook Pro 14 ", "MacBook Pro 14"),
        ("  Nintendo Switch OLED ", "Nintendo Switch OLED"),
        ("  Road Bike Helmet ", "Road Bike Helmet"),
        ("  Pet Carrier Large ", "Pet Carrier Large"),
        ("  Online English Lessons ", "Online English Lessons"),
        ("  Standing Desk Walnut ", "Standing Desk Walnut"),
    ],
)
def test_listing_create_dto_strips_title(title, expected_title):
    dto = ListingCreateDTO(
        title=title,
        description="This description is definitely long enough for title stripping validation.",
        price=100,
        category_id=1,
    )
    assert dto.title == expected_title


@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        (
            {
                "title": "Bad",
                "description": "This description is long enough but title is too short.",
                "price": 100,
                "category_id": 1,
            },
            "title",
        ),
        (
            {
                "title": "Valid title",
                "description": "Too short",
                "price": 100,
                "category_id": 1,
            },
            "description",
        ),
        (
            {
                "title": "Valid title",
                "description": "This description is long enough for validation but price is zero.",
                "price": 0,
                "category_id": 1,
            },
            "price",
        ),
        (
            {
                "title": "Valid title",
                "description": (
                    "This description is long enough for validation but price is negative."
                ),
                "price": -1,
                "category_id": 1,
            },
            "price",
        ),
        (
            {
                "title": "Valid title",
                "description": "This description is long enough for validation but url is invalid.",
                "price": 10,
                "category_id": 1,
                "image_urls": ["not-a-url"],
            },
            "image_urls",
        ),
        (
            {
                "title": "Valid title",
                "description": "",
                "price": 10,
                "category_id": 1,
            },
            "description",
        ),
        (
            {
                "title": "1234",
                "description": "This description is long enough for validation.",
                "price": 10,
                "category_id": 1,
            },
            "title",
        ),
        (
            {
                "title": "Valid title",
                "description": "Too short text",
                "price": 10,
                "category_id": 1,
            },
            "description",
        ),
        (
            {
                "title": "Valid title",
                "description": "This description is long enough for validation.",
                "price": "free",
                "category_id": 1,
            },
            "price",
        ),
        (
            {
                "title": "Valid title",
                "description": "This description is long enough for validation.",
                "price": 10,
                "category_id": 1,
                "image_urls": [
                    "https://images.example.com/1.jpg",
                    "https://images.example.com/2.jpg",
                    "https://images.example.com/3.jpg",
                    "https://images.example.com/4.jpg",
                    "https://images.example.com/5.jpg",
                    "https://images.example.com/6.jpg",
                    "https://images.example.com/7.jpg",
                ],
            },
            "image_urls",
        ),
        (
            {
                "title": "Valid title",
                "description": "This description is long enough for validation.",
                "price": 10,
                "category_id": 1,
                "image_urls": ["ftp://images.example.com/file.jpg"],
            },
            "image_urls",
        ),
    ],
)
def test_listing_create_dto_rejects_invalid_inputs(payload, expected_field):
    with pytest.raises(ValidationError) as exc_info:
        ListingCreateDTO(**payload)
    assert expected_field in str(exc_info.value)


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "Updated title"},
        {"description": "This description is long enough for update validation to pass."},
        {"price": 1},
        {"price": 999.99},
        {"category_id": 42},
        {"image_urls": ["https://images.example.com/updated.jpg"]},
        {"title": "Updated title", "price": 55.5},
        {
            "title": "Desk update",
            "description": "This description is long enough for update validation to pass.",
            "price": 70,
            "category_id": 7,
            "image_urls": [
                "https://images.example.com/a.jpg",
                "https://images.example.com/b.jpg",
            ],
        },
    ],
)
def test_listing_update_dto_accepts_valid_inputs(payload):
    dto = ListingUpdateDTO(**payload)
    for key, value in payload.items():
        actual = getattr(dto, key)
        if key == "image_urls":
            assert [str(url) for url in actual] == value
        else:
            assert actual == value


@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        ({"title": "Bad"}, "title"),
        ({"description": "Too short"}, "description"),
        ({"price": 0}, "price"),
        ({"price": -10}, "price"),
        ({"image_urls": ["notaurl"]}, "image_urls"),
        ({"image_urls": ["ftp://images.example.com/file.jpg"]}, "image_urls"),
        (
            {
                "image_urls": [
                    "https://images.example.com/1.jpg",
                    "https://images.example.com/2.jpg",
                    "https://images.example.com/3.jpg",
                    "https://images.example.com/4.jpg",
                    "https://images.example.com/5.jpg",
                    "https://images.example.com/6.jpg",
                    "https://images.example.com/7.jpg",
                ]
            },
            "image_urls",
        ),
        ({"title": "    "}, "title"),
        ({"description": ""}, "description"),
        ({"price": "free"}, "price"),
    ],
)
def test_listing_update_dto_rejects_invalid_inputs(payload, expected_field):
    with pytest.raises(ValidationError) as exc_info:
        ListingUpdateDTO(**payload)
    assert expected_field in str(exc_info.value)


@pytest.mark.parametrize(
    ("body", "listing_id", "recipient_id"),
    [
        ("Hello", 1, 2),
        ("Still available?", 10, 20),
        ("Can you share more photos?", 2, 3),
        ("What is the final price?", 3, 4),
        ("Can we meet tomorrow?", 4, 5),
        ("Please reserve it for me.", 5, 6),
        ("I can pick it up today.", 6, 7),
        ("Do you have a warranty?", 7, 8),
        ("Can you deliver to Kyiv?", 8, 9),
        ("Interested, please reply.", 9, 10),
    ],
)
def test_message_create_dto_accepts_valid_inputs(body, listing_id, recipient_id):
    dto = MessageCreateDTO(listing_id=listing_id, recipient_id=recipient_id, body=body)
    assert dto.body == body


@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        ({"listing_id": 1, "recipient_id": 2, "body": ""}, "body"),
        ({"listing_id": 1, "recipient_id": 2, "body": "a" * 1001}, "body"),
        ({"listing_id": 1, "recipient_id": 2}, "body"),
        ({"listing_id": "x", "recipient_id": 2, "body": "Hello"}, "listing_id"),
        ({"listing_id": 1, "recipient_id": "x", "body": "Hello"}, "recipient_id"),
        ({"listing_id": None, "recipient_id": 2, "body": "Hello"}, "listing_id"),
        ({"listing_id": 1, "recipient_id": None, "body": "Hello"}, "recipient_id"),
        ({"listing_id": 1, "recipient_id": 2, "body": None}, "body"),
    ],
)
def test_message_create_dto_rejects_invalid_inputs(payload, expected_field):
    with pytest.raises(ValidationError) as exc_info:
        MessageCreateDTO(**payload)
    assert expected_field in str(exc_info.value)


@pytest.mark.parametrize(
    ("approved", "reason"),
    [
        (True, None),
        (False, "Spam"),
        (False, "Wrong category"),
        (False, "Suspicious content"),
        (False, "Duplicate listing"),
        (False, "Missing details"),
    ],
)
def test_moderation_decision_dto_accepts_valid_inputs(approved, reason):
    dto = ModerationDecisionDTO(approved=approved, rejection_reason=reason)
    assert dto.approved is approved


@pytest.mark.parametrize(
    "reason",
    [
        "x" * 256,
        "y" * 300,
        "z" * 500,
        "reason" * 100,
    ],
)
def test_moderation_decision_dto_rejects_too_long_reason(reason):
    with pytest.raises(ValidationError):
        ModerationDecisionDTO(approved=False, rejection_reason=reason)


@pytest.mark.parametrize(
    ("payload", "expected_role"),
    [
        ({"full_name": "Admin User", "role": Role.ADMIN, "is_blocked": False}, Role.ADMIN),
        (
            {"full_name": "Moderator User", "role": Role.MODERATOR, "is_blocked": True},
            Role.MODERATOR,
        ),
        ({"role": Role.USER}, Role.USER),
        ({"is_blocked": False}, None),
        ({"full_name": "Updated Name"}, None),
        ({"full_name": "AB", "role": Role.MODERATOR}, Role.MODERATOR),
        ({"is_blocked": True, "role": Role.USER}, Role.USER),
        ({"full_name": "Seller Updated", "is_blocked": False}, None),
    ],
)
def test_user_admin_update_dto_accepts_valid_inputs(payload, expected_role):
    dto = UserAdminUpdateDTO(**payload)
    assert dto.role == expected_role


@pytest.mark.parametrize(
    ("payload", "expected_field"),
    [
        ({"full_name": "A"}, "full_name"),
        ({"full_name": ""}, "full_name"),
        ({"full_name": " "}, "full_name"),
        ({"role": "superadmin"}, "role"),
        ({"full_name": "A", "role": "moderator"}, "full_name"),
    ],
)
def test_user_admin_update_dto_rejects_invalid_inputs(payload, expected_field):
    with pytest.raises(ValidationError) as exc_info:
        UserAdminUpdateDTO(**payload)
    assert expected_field in str(exc_info.value)


@pytest.mark.parametrize(
    "full_name",
    [
        "Updated User",
        "AB",
        "Buyer Name",
        "Seller Name",
        "Moderator Name",
        "Administrator Name",
        "Very Long But Valid Name",
        "Марія",
    ],
)
def test_user_update_dto_accepts_valid_full_names(full_name):
    dto = UserUpdateDTO(full_name=full_name)
    assert dto.full_name == full_name


@pytest.mark.parametrize("full_name", ["", "A", "X"])
def test_user_update_dto_rejects_invalid_full_names(full_name):
    with pytest.raises(ValidationError):
        UserUpdateDTO(full_name=full_name)


@pytest.mark.parametrize(
    "urls",
    [
        ["https://images.example.com/1.jpg"],
        ["https://images.example.com/1.jpg", "https://images.example.com/2.jpg"],
        [
            "https://images.example.com/1.jpg",
            "https://images.example.com/2.jpg",
            "https://images.example.com/3.jpg",
        ],
        ["https://images.example.com/item.webp"],
        ["https://cdn.example.com/item.png"],
        ["https://assets.example.com/photo.jpeg"],
    ],
)
def test_upload_batch_dto_accepts_valid_urls(urls):
    dto = UploadImageBatchDTO(files=[{"url": url} for url in urls])
    assert len(dto.files) == len(urls)


@pytest.mark.parametrize("files", [[{"url": None}]])
def test_upload_batch_dto_rejects_invalid_urls(files):
    with pytest.raises(ValidationError):
        UploadImageBatchDTO(files=files)
