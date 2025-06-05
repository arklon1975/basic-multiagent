import pytest
from app.validators import (
    validate_url,
    validate_prompt,
    sanitize_input,
    validate_api_key,
    ValidationError
)

def test_validate_url():
    # URLs válidas
    assert validate_url("https://example.com")
    assert validate_url("http://sub.example.com/path")
    
    # URLs inválidas
    assert not validate_url("not-a-url")
    assert not validate_url("ftp://invalid")
    assert not validate_url("")

def test_validate_prompt():
    # Prompts válidos
    assert validate_prompt("Valid prompt")
    assert validate_prompt("A" * 1000)  # Máxima longitud
    
    # Prompts inválidos
    assert not validate_prompt("")
    assert not validate_prompt(None)
    assert not validate_prompt("A" * 1001)  # Excede longitud máxima
    assert not validate_prompt("<script>alert('xss')</script>")

def test_sanitize_input():
    # Entradas válidas
    assert sanitize_input("Normal text") == "Normal text"
    assert sanitize_input("  Spaces  ") == "Spaces"
    
    # Entradas que necesitan sanitización
    assert sanitize_input("<p>HTML</p>") == "HTML"
    assert sanitize_input("Multiple   spaces") == "Multiple spaces"
    assert sanitize_input("Control\x00chars") == "Controlchars"
    
    # Entradas inválidas
    assert sanitize_input("") is None
    assert sanitize_input(None) is None

def test_validate_api_key():
    # API keys válidas
    assert validate_api_key("sk-1234567890abcdefghijklmnopqrstuvwxyz")
    
    # API keys inválidas
    assert not validate_api_key("")
    assert not validate_api_key(None)
    assert not validate_api_key("invalid-key")
    assert not validate_api_key("sk-")  # Muy corta 