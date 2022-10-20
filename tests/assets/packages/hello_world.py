from steamship.invocable import InvocableResponse, PackageService, create_handler, get, post


class HelloWorld(PackageService):
    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        return InvocableResponse(string=f"Hello, {name}")

    @get("workspace")
    def workspace(self) -> InvocableResponse:
        return InvocableResponse(string=self.client.config.workspace_id)


handler = create_handler(HelloWorld)
