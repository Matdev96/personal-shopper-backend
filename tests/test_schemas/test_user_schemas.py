import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserResponse


class TestUserCreateSchema:
    """Testes para schema UserCreate."""
    
    def test_valid_user_creation(self):
        """Testar criação válida de usuário."""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "SecurePass123!",
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.password == "SecurePass123!"
    
    def test_invalid_email(self):
        """Testar email inválido."""
        user_data = {
            "email": "invalid-email",
            "full_name": "Test User",
            "password": "SecurePass123!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "email" in str(exc_info.value).lower()
    
    def test_password_too_short(self):
        """Testar senha muito curta."""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "Short1!",  # Menos de 8 caracteres
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "password" in str(exc_info.value).lower()
    
    def test_password_without_uppercase(self):
        """Testar senha sem letra maiúscula."""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "securepass123!",  # Sem maiúscula
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "maiúscula" in str(exc_info.value).lower()
    
    def test_password_without_number(self):
        """Testar senha sem número."""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "SecurePass!",  # Sem número
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "número" in str(exc_info.value).lower()
    
    def test_password_without_special_char(self):
        """Testar senha sem caractere especial."""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "SecurePass123",  # Sem caractere especial
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "especial" in str(exc_info.value).lower()
    
    def test_full_name_too_short(self):
        """Testar nome muito curto."""
        user_data = {
            "email": "test@example.com",
            "full_name": "AB",  # Menos de 3 caracteres
            "password": "SecurePass123!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "full_name" in str(exc_info.value).lower()
    
    def test_full_name_too_long(self):
        """Testar nome muito longo."""
        user_data = {
            "email": "test@example.com",
            "full_name": "A" * 101,  # Mais de 100 caracteres
            "password": "SecurePass123!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "full_name" in str(exc_info.value).lower()


class TestUserLoginSchema:
    """Testes para schema UserLogin."""
    
    def test_valid_login(self):
        """Testar login válido."""
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
        }
        login = UserLogin(**login_data)
        assert login.email == "test@example.com"
        assert login.password == "SecurePass123!"
    
    def test_invalid_email_login(self):
        """Testar email inválido no login."""
        login_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
        }
        with pytest.raises(ValidationError):
            UserLogin(**login_data)
    
    def test_missing_password(self):
        """Testar login sem senha."""
        login_data = {
            "email": "test@example.com",
        }
        with pytest.raises(ValidationError):
            UserLogin(**login_data)


class TestUserUpdateSchema:
    """Testes para schema UserUpdate."""
    
    def test_valid_update_email(self):
        """Testar atualização válida de email."""
        update_data = {
            "email": "newemail@example.com",
        }
        update = UserUpdate(**update_data)
        assert update.email == "newemail@example.com"
    
    def test_valid_update_password(self):
        """Testar atualização válida de senha."""
        update_data = {
            "password": "NewSecurePass123!",
        }
        update = UserUpdate(**update_data)
        assert update.password == "NewSecurePass123!"
    
    def test_update_all_fields(self):
        """Testar atualização de todos os campos."""
        update_data = {
            "email": "newemail@example.com",
            "full_name": "New Name",
            "password": "NewSecurePass123!",
        }
        update = UserUpdate(**update_data)
        assert update.email == "newemail@example.com"
        assert update.full_name == "New Name"
        assert update.password == "NewSecurePass123!"
    
    def test_update_empty(self):
        """Testar atualização vazia (todos os campos None)."""
        update_data = {}
        update = UserUpdate(**update_data)
        assert update.email is None
        assert update.full_name is None
        assert update.password is None