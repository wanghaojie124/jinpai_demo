import requests

BASE_URL = "https://api.thenextleg.io/v2"


class TNL:
    def __init__(self, token):
        self.token = token

    def create_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def imagine(self, prompt, ref="", webhook_override=""):
        """
        Imagine an image based on a prompt.
        ARGS:
            prompt: str - The prompt to use.
            ref: str - A reference string passed back in the webhook
            webhook_override: str - A webhook to override the default webhook.
        """
        request = {
            "msg": prompt,
            "ref": ref,
            "webhookOverride": webhook_override,
        }

        res = requests.post(
            f"{BASE_URL}/imagine", json=request, headers=self.create_headers()
        )
        res.close()
        return res.json()

    def img2img(self, prompt, img_url, ref="", webhook_override=""):
        """
        Perform an image to image operation.
        ARGS:
            prompt: str - The prompt to use.
            img_url: str - The image to use.
            ref: str - A reference string passed back in the webhook
            webhook_override: str - A webhook to override the default webhook.
        """
        request = {
            "msg": f"{img_url} {prompt}",
            "ref": ref,
            "webhookOverride": webhook_override,
        }

        res = requests.post(
            f"{BASE_URL}/imagine", json=request, headers=self.create_headers()
        )
        res.close()
        return res.json()

    def describe(self, img_url, ref="", webhook_override=""):
        """
        Describe an image.
        ARGS:
            img_url: str - The image to describe.
            ref: str - A reference string passed back in the webhook
            webhook_override: str - A webhook to override the default webhook.
        """
        request = {
            "url": img_url,
            "ref": ref,
            "webhookOverride": webhook_override,
        }

        res = requests.post(
            f"{BASE_URL}/imagine", json=request, headers=self.create_headers()
        )
        return res.json()

    def button(self, button, button_message_id, ref="", webhook_override=""):
        """
        Press a button.
        ARGS:
            button: str - The button to press.
            button_message_id: str - The message id of the button.
            ref: str - A reference string passed back in the webhook
            webhook_override: str - A webhook to override the default webhook.
        """
        request = {
            "button": button,
            "buttonMessageId": button_message_id,
            "ref": ref,
            "webhookOverride": webhook_override,
        }

        res = requests.post(
            f"{BASE_URL}/button", json=request, headers=self.create_headers()
        )
        return res.json()

    def get_seed(self, message_id):
        """
        Get the seed of a message.
        ARGS:
            message_id: str - The message id of the message.
        """
        request = {
            "messageId": message_id,
        }

        res = requests.post(
            f"{BASE_URL}/seed", json=request, headers=self.create_headers()
        )
        return res.json()

    def slash_command(self, slash_command, ref="", webhook_override=""):
        """
        Perform a slash command.
        ARGS:
            slash_command: str - The slash command to perform.
            ref: str - A reference string passed back in the webhook
            webhook_override: str - A webhook to override the default webhook.
        """
        request = {
            "cmd": slash_command,
            "ref": ref,
            "webhookOverride": webhook_override,
        }

        res = requests.post(
            f"{BASE_URL}/slash-commands", json=request, headers=self.create_headers()
        )
        return res.json()

    def get_settings(self):
        """
        Get an account setting.
        """
        res = requests.get(f"{BASE_URL}/settings", headers=self.create_headers())
        return res.json()

    def set_settings(self, setting, ref="", webhook_override=""):
        """
        Set an account settings.
        ARGS:
            setting: str - The setting to set.
            ref: str - A reference string passed back in the webhook
            webhook_override: str - A webhook to override the default webhook.
        """
        request = {
            "settingsToggle": setting,
            "ref": ref,
            "webhookOverride": webhook_override,
        }

        res = requests.post(
            f"{BASE_URL}/settings", json=request, headers=self.create_headers()
        )
        return res.json()

    def get_info(self, ref="", webhook_override=""):
        """
        Get the info of the account.
        ARGS:
            ref: str - A reference string passed back in the webhook
            webhook_override: str - A webhook to override the default webhook.
        """
        request = {
            "ref": ref,
            "webhookOverride": webhook_override,
        }

        res = requests.post(
            f"{BASE_URL}/info", json=request, headers=self.create_headers()
        )
        return res.json()

    def get_message_and_progress(self, message_id, expire_mins):
        """
        Get the message and progress of a message.
        ARGS:
            message_id: str - The message id of the message.
            expire_mins: int - The time to live for the message.
        """
        url = f"{BASE_URL}/message/{message_id}"
        if expire_mins:
            url += f"?expireMins={expire_mins}"
        res = requests.get(
            f"{BASE_URL}/message/{message_id}", headers=self.create_headers()
        )
        res.close()
        return res.json()


if __name__ == '__main__':
    tnl = TNL("f9db7b75-eade-459a-bc05-1e6504007176")
    # message = tnl.img2img("https://comiximg-1311503813.cos.ap-beijing.myqcloud.com/server/to_mj/1690865616787.png", "test")
    # print(message)
    resp = tnl.get_message_and_progress("rt2AFi5OG5PEnZjicJ8H", expire_mins=4)
    print(resp)