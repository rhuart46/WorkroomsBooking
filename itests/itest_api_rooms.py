from base import IntegrationTest


class TestApiRooms(IntegrationTest):
    """Test the behaviour of the endpoints of the namespace /rooms."""

    def test_get_all_rooms_should_succeed(self):
        expected_room_codes = ["room" + str(i) for i in range(10)]

        response = self.rooms_api_get()
        self.assertEqual(response.status_code, 200)

        response_room_codes = [item["code"] for item in response.json]
        self.assertEqual(response_room_codes, expected_room_codes)
