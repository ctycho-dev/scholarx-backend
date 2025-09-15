import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from fastapi import HTTPException
from app.domain.user.schema import UserOut, UserCreate, UserUpdate

class TestUserEndpoints:
    """Test suite for user endpoints."""

    @pytest.mark.asyncio
    async def test_get_user_success(self, client: AsyncClient, mock_user_service, mock_current_user):
        """Test successful user retrieval."""
        # Arrange
        mock_user_service.has_profile.return_value = True
        
        # Act
        response = await client.get("/users/me/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == mock_current_user.email
        assert data["has_profile"] is True
        mock_user_service.has_profile.assert_called_once_with(mock_current_user.id)

    @pytest.mark.asyncio
    async def test_get_user_service_error(self, client: AsyncClient, mock_user_service):
        """Test user retrieval with service error."""
        # Arrange
        mock_user_service.has_profile.side_effect = ValueError("Service error")
        
        # Act
        response = await client.get("/users/me/")
        
        # Assert
        assert response.status_code == 400
        assert "Service error" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_user_success(self, client: AsyncClient, mock_user_service):
        """Test successful user creation."""
        # Arrange
        user_data = {
            "email": "new@example.com",
            "username": "newuser",
            "privy_id": "new_privy_id"
        }
        expected_user = UserOut(
            id=2,
            email="new@example.com",
            username="newuser",
            privy_id="new_privy_id",
            has_profile=True
        )
        mock_user_service.create_user.return_value = expected_user
        
        # Act
        response = await client.post("/users/", json=user_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        mock_user_service.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_validation_error(self, client: AsyncClient, mock_user_service):
        """Test user creation with invalid data."""
        # Arrange
        invalid_data = {"email": "invalid-email"}  # Missing required fields
        
        # Act
        response = await client.post("/users/", json=invalid_data)
        
        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_user_service_error(self, client: AsyncClient, mock_user_service):
        """Test user creation with service error."""
        # Arrange
        user_data = {
            "email": "new@example.com",
            "username": "newuser",
            "privy_id": "new_privy_id"
        }
        mock_user_service.create_user.side_effect = ValueError("User already exists")
        
        # Act
        response = await client.post("/users/", json=user_data)
        
        # Assert
        assert response.status_code == 400
        assert "User already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_user_success(self, client: AsyncClient, mock_user_service, mock_current_user):
        """Test successful user update."""
        # Arrange
        update_data = {"bio": "Updated bio", "username": "updated_username"}
        updated_user = UserOut(
            id=mock_current_user.id,
            email=mock_current_user.email,
            privy_id=mock_current_user.privy_id,
            has_profile=True
        )
        mock_user_service.update.return_value = updated_user
        mock_user_service.has_profile.return_value = True
        
        # Act
        response = await client.patch("/users/", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Updated bio"
        assert data["username"] == "updated_username"
        assert data["has_profile"] is True
        mock_user_service.update.assert_called_once_with(mock_current_user.id, update_data)

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client: AsyncClient, mock_user_service, mock_current_user):
        """Test user update when user not found."""
        # Arrange
        update_data = {"bio": "Updated bio"}
        mock_user_service.update.side_effect = HTTPException(status_code=404, detail="User not found")
        
        # Act
        response = await client.patch("/users/", json=update_data)
        
        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_empty_data(self, client: AsyncClient, mock_user_service, mock_current_user):
        """Test user update with empty data."""
        # Arrange
        update_data = {}
        updated_user = mock_current_user
        mock_user_service.update.return_value = updated_user
        mock_user_service.has_profile.return_value = True
        
        # Act
        response = await client.patch("/users/", json=update_data)
        
        # Assert
        assert response.status_code == 200
        mock_user_service.update.assert_called_once_with(mock_current_user.id, update_data)


class TestUserEndpointsIntegration:
    """Integration tests with real database."""

    @pytest.mark.asyncio
    async def test_get_user_with_real_db(self, test_db_session, mock_current_user):
        """Test user retrieval with real database session."""
        # This would test with actual UserService and repository
        # using the test_db_session fixture
        pass
