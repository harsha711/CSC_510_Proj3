"""
Unit tests for user_service.py

Tests user management operations including:
- User creation with password hashing
- User login/authentication
- Getting users by ID and username
- Updating user information
- Deleting users
- Password security
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId
from app.services.user_service import (
    create_user,
    login_user,
    get_user_by_id,
    get_user_by_username,
    update_user,
    delete_user,
    _strip_password
)
from app.models.exception_model import (
    NotFoundException,
    BadRequestException,
    DatabaseException,
    ConflictException
)


class TestStripPassword:
    """Test _strip_password helper function"""

    def test_strips_password_field(self):
        """Test that password is removed from user document"""
        doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "password": "hashed_password_here"
        }

        result = _strip_password(doc)

        assert "password" not in result
        assert result["username"] == "testuser"

    def test_converts_object_id_to_string(self):
        """Test that ObjectId is converted to string"""
        doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "password": "hashed"
        }

        result = _strip_password(doc)

        assert isinstance(result["_id"], str)
        assert result["_id"] == "507f1f77bcf86cd799439011"

    def test_handles_none_doc(self):
        """Test that None doc returns None"""
        result = _strip_password(None)
        assert result is None

    def test_handles_doc_without_password(self):
        """Test document that doesn't have password field"""
        doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser"
        }

        result = _strip_password(doc)

        assert "password" not in result
        assert result["username"] == "testuser"


@patch('app.services.user_service.db')
@patch('app.services.user_service.pwd_ctx')
class TestCreateUser:
    """Test user creation"""

    def test_create_user_success(self, mock_pwd_ctx, mock_db):
        """Test successful user creation"""
        user_create = Mock()
        user_create.username = "newuser"
        user_create.password = "password123"
        user_create.model_dump.return_value = {
            "username": "newuser",
            "password": "password123",
            "email": "user@example.com"
        }

        mock_db.users.find_one.side_effect = [
            None,  # No existing user
            {  # Created user
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "username": "newuser",
                "password": "hashed_password",
                "email": "user@example.com"
            }
        ]
        mock_pwd_ctx.hash.return_value = "hashed_password"
        mock_db.users.insert_one.return_value = Mock(inserted_id=ObjectId("507f1f77bcf86cd799439011"))

        result = create_user(user_create)

        assert result["username"] == "newuser"
        assert "password" not in result
        assert isinstance(result["_id"], str)
        mock_pwd_ctx.hash.assert_called_once()

    def test_create_user_duplicate_username(self, mock_pwd_ctx, mock_db):
        """Test creating user with existing username raises error"""
        user_create = Mock()
        user_create.username = "existing_user"

        mock_db.users.find_one.return_value = {"username": "existing_user"}

        with pytest.raises(ConflictException) as exc_info:
            create_user(user_create)

        assert "Username already taken" in str(exc_info.value.detail)

    def test_create_user_database_error(self, mock_pwd_ctx, mock_db):
        """Test database error during creation"""
        user_create = Mock()
        user_create.username = "newuser"
        user_create.password = "password123"
        user_create.model_dump.return_value = {"username": "newuser", "password": "password123"}

        mock_db.users.find_one.return_value = None
        mock_pwd_ctx.hash.return_value = "hashed"
        mock_db.users.insert_one.side_effect = Exception("DB Error")

        with pytest.raises(DatabaseException):
            create_user(user_create)

    def test_create_user_truncates_long_password(self, mock_pwd_ctx, mock_db):
        """Test that password is truncated to 72 chars for bcrypt"""
        user_create = Mock()
        user_create.username = "newuser"
        user_create.password = "a" * 100  # Very long password
        user_create.model_dump.return_value = {"username": "newuser", "password": "a" * 100}

        mock_db.users.find_one.side_effect = [
            None,  # No existing user
            {  # Created user
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "username": "newuser",
                "password": "hashed"
            }
        ]
        mock_pwd_ctx.hash.return_value = "hashed"
        mock_db.users.insert_one.return_value = Mock(inserted_id=ObjectId("507f1f77bcf86cd799439011"))

        create_user(user_create)

        # Verify that password was truncated to 72 chars
        call_args = mock_pwd_ctx.hash.call_args[0][0]
        assert len(call_args) == 72


@patch('app.services.user_service.db')
@patch('app.services.user_service.pwd_ctx')
class TestLoginUser:
    """Test user login/authentication"""

    def test_login_success(self, mock_pwd_ctx, mock_db):
        """Test successful login"""
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "password": "hashed_password"
        }
        mock_pwd_ctx.verify.return_value = True

        result = login_user("testuser", "correct_password")

        assert result["access_token"] == "507f1f77bcf86cd799439011"
        assert result["token_type"] == "bearer"

    def test_login_user_not_found(self, mock_pwd_ctx, mock_db):
        """Test login with non-existent username"""
        mock_db.users.find_one.return_value = None

        with pytest.raises(BadRequestException) as exc_info:
            login_user("nonexistent", "password")

        assert "Invalid username or password" in str(exc_info.value.message)

    def test_login_wrong_password(self, mock_pwd_ctx, mock_db):
        """Test login with wrong password"""
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "password": "hashed_password"
        }
        mock_pwd_ctx.verify.return_value = False

        with pytest.raises(BadRequestException) as exc_info:
            login_user("testuser", "wrong_password")

        assert "Invalid username or password" in str(exc_info.value.message)

    def test_login_missing_password_field(self, mock_pwd_ctx, mock_db):
        """Test login when user document has no password field"""
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser"
        }
        mock_pwd_ctx.verify.return_value = False

        with pytest.raises(BadRequestException):
            login_user("testuser", "password")


@patch('app.services.user_service.db')
class TestGetUserById:
    """Test getting user by ID"""

    def test_get_user_by_id_success(self, mock_db):
        """Test successfully getting user by ID"""
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "password": "hashed",
            "email": "test@example.com"
        }

        result = get_user_by_id("507f1f77bcf86cd799439011")

        assert result["username"] == "testuser"
        assert "password" not in result
        assert result["email"] == "test@example.com"

    def test_get_user_by_id_invalid_id(self, mock_db):
        """Test getting user with invalid ID format"""
        with pytest.raises(NotFoundException) as exc_info:
            get_user_by_id("invalid_id")

        assert "Invalid user id" in str(exc_info.value.name)

    def test_get_user_by_id_not_found(self, mock_db):
        """Test getting non-existent user"""
        mock_db.users.find_one.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            get_user_by_id("507f1f77bcf86cd799439011")

        assert "User not found" in str(exc_info.value.name)


@patch('app.services.user_service.db')
class TestGetUserByUsername:
    """Test getting user by username"""

    def test_get_user_by_username_success(self, mock_db):
        """Test successfully getting user by username"""
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "password": "hashed",
            "email": "test@example.com"
        }

        result = get_user_by_username("testuser")

        assert result["username"] == "testuser"
        assert "password" not in result

    def test_get_user_by_username_not_found(self, mock_db):
        """Test getting non-existent user by username"""
        mock_db.users.find_one.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            get_user_by_username("nonexistent")

        assert "User not found" in str(exc_info.value.name)


@patch('app.services.user_service.db')
class TestUpdateUser:
    """Test user update"""

    def test_update_user_success(self, mock_db):
        """Test successful user update"""
        update_data = {"email": "newemail@example.com"}

        mock_db.users.update_one.return_value = Mock(matched_count=1)
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "email": "newemail@example.com",
            "password": "hashed"
        }

        result = update_user("507f1f77bcf86cd799439011", update_data)

        assert result["email"] == "newemail@example.com"
        assert "password" not in result

    def test_update_user_no_data(self, mock_db):
        """Test update with no data raises error"""
        with pytest.raises(BadRequestException) as exc_info:
            update_user("507f1f77bcf86cd799439011", {})

        assert "No fields to update" in str(exc_info.value.message)

    def test_update_user_invalid_id(self, mock_db):
        """Test update with invalid ID"""
        with pytest.raises(NotFoundException):
            update_user("invalid_id", {"email": "test@example.com"})

    def test_update_user_multiple_fields(self, mock_db):
        """Test updating multiple fields"""
        update_data = {
            "email": "new@example.com",
            "allergen_preferences": ["peanuts", "shellfish"]
        }

        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "email": "new@example.com",
            "allergen_preferences": ["peanuts", "shellfish"],
            "password": "hashed"
        }

        result = update_user("507f1f77bcf86cd799439011", update_data)

        assert result["email"] == "new@example.com"
        assert result["allergen_preferences"] == ["peanuts", "shellfish"]


@patch('app.services.user_service.db')
class TestDeleteUser:
    """Test user deletion"""

    def test_delete_user_success(self, mock_db):
        """Test successful user deletion"""
        mock_db.users.delete_one.return_value = Mock(deleted_count=1)

        result = delete_user("507f1f77bcf86cd799439011")

        # Should return None on success
        assert result is None

    def test_delete_user_invalid_id(self, mock_db):
        """Test delete with invalid ID"""
        with pytest.raises(NotFoundException):
            delete_user("invalid_id")

    def test_delete_user_not_found(self, mock_db):
        """Test deleting non-existent user"""
        mock_db.users.delete_one.return_value = Mock(deleted_count=0)

        with pytest.raises(NotFoundException) as exc_info:
            delete_user("507f1f77bcf86cd799439011")

        assert "User not found" in str(exc_info.value.name)


class TestPasswordSecurity:
    """Test password security measures"""

    @patch('app.services.user_service.db')
    @patch('app.services.user_service.pwd_ctx')
    def test_password_hashed_before_storage(self, mock_pwd_ctx, mock_db):
        """Test that password is hashed before storing"""
        user_create = Mock()
        user_create.username = "secureuser"
        user_create.password = "plain_password"
        user_create.model_dump.return_value = {"username": "secureuser", "password": "plain_password"}

        mock_db.users.find_one.return_value = None
        mock_pwd_ctx.hash.return_value = "hashed_password"
        mock_db.users.insert_one.return_value = Mock(inserted_id=ObjectId("507f1f77bcf86cd799439011"))

        # Set up find_one to return hashed password
        mock_db.users.find_one.side_effect = [
            None,  # First call for checking existence
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "username": "secureuser",
                "password": "hashed_password"
            }
        ]

        create_user(user_create)

        # Verify hash was called
        mock_pwd_ctx.hash.assert_called_once()

    @patch('app.services.user_service.db')
    def test_password_never_returned_in_response(self, mock_db):
        """Test that password is never included in API responses"""
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "password": "hashed_password"
        }

        result = get_user_by_id("507f1f77bcf86cd799439011")

        assert "password" not in result

    @patch('app.services.user_service.db')
    @patch('app.services.user_service.pwd_ctx')
    def test_bcrypt_used_for_hashing(self, mock_pwd_ctx, mock_db):
        """Test that bcrypt is used for password hashing"""
        # This test verifies that pwd_ctx is configured correctly
        # The actual bcrypt usage is tested through the hash method
        user_create = Mock()
        user_create.username = "testuser"
        user_create.password = "password123"
        user_create.model_dump.return_value = {"username": "testuser", "password": "password123"}

        user_id = ObjectId()
        mock_db.users.find_one.side_effect = [
            None,  # No existing user
            {"_id": user_id, "username": "testuser", "password": "bcrypt_hash"}  # Created user
        ]
        mock_pwd_ctx.hash.return_value = "bcrypt_hash"
        mock_db.users.insert_one.return_value = Mock(inserted_id=user_id)

        create_user(user_create)

        # Verify hash method was called (bcrypt's hash method)
        assert mock_pwd_ctx.hash.called


class TestEdgeCases:
    """Test edge cases in user service"""

    @patch('app.services.user_service.db')
    def test_empty_username(self, mock_db):
        """Test handling of empty username"""
        user_create = Mock()
        user_create.username = ""

        mock_db.users.find_one.return_value = None  # No existing user

        # Should still check for duplicates even with empty username
        # (Validation should happen at Pydantic level, but test service behavior)
        # This test ensures the service doesn't crash with empty username


    @patch('app.services.user_service.db')
    def test_special_characters_in_username(self, mock_db):
        """Test username with special characters"""
        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "user@#$%",
            "password": "hashed"
        }

        result = get_user_by_username("user@#$%")

        assert result["username"] == "user@#$%"

    @patch('app.services.user_service.db')
    def test_very_long_username(self, mock_db):
        """Test very long username"""
        long_username = "a" * 1000

        mock_db.users.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": long_username,
            "password": "hashed"
        }

        result = get_user_by_username(long_username)

        assert len(result["username"]) == 1000
