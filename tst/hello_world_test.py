from hello_world import hello_world


class TestHelloWorld:

    def test_prints_hello_world(self):
        result = hello_world()
        assert "Hello World" in result
