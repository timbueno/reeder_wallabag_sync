import pytest
from wallabag_sync.utils import hash_url

def test_hash_url_string():
    """Test hashing a URL string."""
    url = "https://example.com/article"
    hash_value = hash_url(url)
    
    # Verify the hash is a 40-character hexadecimal string
    assert len(hash_value) == 40
    assert all(c in '0123456789abcdef' for c in hash_value)
    
    # Verify the hash is consistent
    assert hash_url(url) == hash_value

def test_hash_url_bytes():
    """Test hashing a URL as bytes."""
    url = b"https://example.com/article"
    hash_value = hash_url(url)
    
    # Verify the hash is a 40-character hexadecimal string
    assert len(hash_value) == 40
    assert all(c in '0123456789abcdef' for c in hash_value)
    
    # Verify the hash is the same as the string version
    assert hash_value == hash_url(url.decode('utf-8'))

def test_hash_url_invalid_type():
    """Test hashing with invalid input type."""
    with pytest.raises(TypeError) as exc_info:
        hash_url(123)  # type: ignore
    
    assert "URL must be a string or bytes" in str(exc_info.value)

def test_hash_url_consistency():
    """Test that the same URL always produces the same hash."""
    url = "https://example.com/article"
    hash1 = hash_url(url)
    hash2 = hash_url(url)
    hash3 = hash_url(url.encode('utf-8'))
    
    assert hash1 == hash2 == hash3

def test_hash_url_different_urls():
    """Test that different URLs produce different hashes."""
    url1 = "https://example.com/article1"
    url2 = "https://example.com/article2"
    
    assert hash_url(url1) != hash_url(url2) 