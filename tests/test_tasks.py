from unittest.mock import MagicMock, patch


def test_fetch_weather_for_location_success():
    from backend.tasks.weather import fetch_weather_for_location

    mock_location = MagicMock()
    mock_location.city = "London"
    mock_location.country = "GB"

    with (
        patch("backend.tasks.weather.SessionLocal") as mock_session,
        patch("backend.tasks.weather.get_coordinates", return_value=(51.5, -0.1)),
        patch(
            "backend.tasks.weather.fetch_current_weather",
            return_value={
                "temperature": 15.0,
                "feels_like": 13.0,
                "humidity": 70,
                "wind_speed": 10.0,
                "description": "Partly cloudy",
            },
        ),
    ):
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        first_result = MagicMock()
        first_result.scalar_one_or_none.return_value = mock_location
        second_result = MagicMock()
        second_result.scalar_one_or_none.return_value = None
        mock_db.execute.side_effect = [first_result, second_result]

        fetch_weather_for_location.apply(args=[1])

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


def test_fetch_weather_for_location_not_found():
    from backend.tasks.weather import fetch_weather_for_location

    with patch("backend.tasks.weather.SessionLocal") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        fetch_weather_for_location.apply(args=[99999])

        mock_db.add.assert_not_called()


def test_fetch_weather_skips_if_recent_record():
    from backend.tasks.weather import fetch_weather_for_location

    mock_location = MagicMock()
    mock_location.city = "London"
    mock_location.country = "GB"

    mock_recent = MagicMock()

    with (
        patch("backend.tasks.weather.SessionLocal") as mock_session,
        patch("backend.tasks.weather.get_coordinates") as mock_coords,
    ):
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [mock_location, mock_recent]

        fetch_weather_for_location.apply(args=[1])

        mock_coords.assert_not_called()
        mock_db.add.assert_not_called()


def test_fetch_all_weather():
    from backend.tasks.weather import fetch_all_weather

    mock_location = MagicMock()
    mock_location.id = 1

    with (
        patch("backend.tasks.weather.SessionLocal") as mock_session,
        patch("backend.tasks.weather.fetch_weather_for_location") as mock_task,
    ):
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_location]

        fetch_all_weather.apply()

        mock_task.delay.assert_called_once_with(1)


def test_send_welcome_email_task():
    from backend.tasks.email import send_welcome_email

    with patch("backend.tasks.email.send_email") as mock_send:
        send_welcome_email.apply(args=["testuser", "test@example.com"])
        mock_send.assert_called_once_with(username="testuser", email="test@example.com")
