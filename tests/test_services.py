from unittest.mock import MagicMock, patch


def test_weather_code_to_description():
    from backend.services.weather import _weather_code_to_description

    assert _weather_code_to_description(0) == "Clear sky"
    assert _weather_code_to_description(3) == "Overcast"
    assert _weather_code_to_description(63) == "Moderate rain"
    assert _weather_code_to_description(999) == "Unknown"


def test_get_coordinates_success():
    from backend.services.weather import get_coordinates

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [{"latitude": 51.5, "longitude": -0.1}]
    }

    with patch("backend.services.weather.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        lat, lon = get_coordinates("London", "GB")

    assert lat == 51.5
    assert lon == -0.1


def test_get_coordinates_not_found():
    from backend.services.weather import get_coordinates

    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}

    with patch("backend.services.weather.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        try:
            get_coordinates("InvalidCity", "XX")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


def test_fetch_current_weather():
    from backend.services.weather import fetch_current_weather

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 15.0,
            "apparent_temperature": 13.0,
            "relative_humidity_2m": 70,
            "wind_speed_10m": 10.0,
            "weather_code": 1,
        }
    }

    with patch("backend.services.weather.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        result = fetch_current_weather(51.5, -0.1)

    assert result["temperature"] == 15.0
    assert result["feels_like"] == 13.0
    assert result["humidity"] == 70
    assert result["wind_speed"] == 10.0
    assert result["description"] == "Mainly clear"


def test_send_email_service():
    from backend.services.email import send_email

    with patch("backend.services.email.resend.Emails.send") as mock_send:
        send_email(username="testuser", email="test@example.com")
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args["to"] == "test@example.com"
        assert "testuser" in call_args["html"]
