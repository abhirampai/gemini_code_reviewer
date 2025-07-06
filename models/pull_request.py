from pydantic import BaseModel
from typing import Dict, Any
from github import Auth, GithubIntegration
from config import get_settings
from google import genai

auth = Auth.AppAuth(get_settings().GITHUB_APP_ID, get_settings().GITHUB_PRIVATE_KEY)
gi = GithubIntegration(auth=auth)
installation = gi.get_installations()[0]
g = installation.get_github_for_installation()

gemini_client: genai.Client = genai.Client(api_key=get_settings().GEMINI_API_KEY)

class ReviewComment(BaseModel):
    path: str
    body: str
    line: int
    side: str
    start_line: int
    start_side: str

class PullRequest(BaseModel):
    id: int
    number: int
    repository: Dict[str, Any]

    @classmethod
    def from_github_event(cls, event: any):
        payload = event.get("pull_request")
        return cls(
            id=payload["id"],
            number=payload["number"],
            repository=event.get("repository")
        )

    def gemini_review_request(self):
        repo = g.get_repo(self.repository["full_name"])
        pull_request = repo.get_pull(self.number)

        review_comments = []

        for file_data in pull_request.get_files():
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
                You are a helpful assistant that reviews code and comments on a pull request.
                Please review the following code:
                {file_data.patch}
                """,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[ReviewComment]
                }
            )
            review_comments_for_the_file = response.parsed
            for review_comment in review_comments_for_the_file:
                review_comments.append({
                    "path": file_data.filename,
                    **review_comment.__dict__
                })

        self.post_review_comments(pull_request, review_comments)
    
    def post_review_comments(self, pull_request, review_comments: list[dict, any]):
        pull_request.create_review(
            body="Please review the following suggestions",
            event="COMMENT",
            comments=review_comments
        )
