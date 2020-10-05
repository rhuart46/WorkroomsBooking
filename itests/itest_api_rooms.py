from base import IntegrationTest


class TestApiRooms(IntegrationTest):
    """Test the behaviour of the endpoints of the namespace /rooms."""

    #
    # Tests on listing rooms (/rooms):
    #
    def test_get_all_rooms_should_succeed(self):
        expected_room_codes = ["room" + str(i) for i in range(10)]

        response = self.rooms_api_get()
        self.assertEqual(response.status_code, 200)

        response_room_codes = [item["code"] for item in response.json]
        self.assertEqual(response_room_codes, expected_room_codes)

    #
    # Tests on GETting one room (/rooms/<code>):
    #
    def test_getting_one_room_with_correct_id_should_succeed(self):
        room_code = "room2"
        expected_room_data = {
            "code": room_code,
            "name": "Salle Blaise Pascal",
            "floor": 1,
            "capacity": 20,
        }

        response = self.rooms_api_get(f"/{room_code}")
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_room_data, response.json)


