from pydantic import BaseModel
from typing import Dict, Any
from github import Auth, GithubIntegration
from config import get_settings
from google import genai
from utils.diff_checker import find_line_info

auth = Auth.AppAuth(get_settings().GITHUB_APP_ID, get_settings().GITHUB_PRIVATE_KEY)
gi = GithubIntegration(auth=auth)
installation = gi.get_installations()[0]
g = installation.get_github_for_installation()

gemini_client: genai.Client = genai.Client(api_key=get_settings().GEMINI_API_KEY)


class ReviewComment(BaseModel):
    path: str
    body: str
    line: str

    def to_dict(self):
        self.model_dump()


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
            repository=event.get("repository"),
        )

    def gemini_review_request(self):
        repo = g.get_repo(self.repository["full_name"])
        pull_request = repo.get_pull(self.number)

        review_comments = []

        for file_data in pull_request.get_files():
            review_comments_for_the_file = self.generate_review(file_data.patch)
            for review_comment in review_comments_for_the_file:
                line_changed = review_comment.line
                review_comment_dict = review_comment.to_dict
                review_comment_dict.pop("line")
                review_comments.append(
                    {
                        **review_comment_dict,
                        "path": file_data.filename,
                        **find_line_info(file_data.patch, line_changed),
                    }
                )
            if len(review_comments) >= 50:
                break

        self.post_review_comments(pull_request, review_comments)

    def post_review_comments(self, pull_request, review_comments: list[dict, any]):
        pull_request.create_review(
            body="Please review the following suggestions",
            event="COMMENT",
            comments=review_comments,
        )

    def generate_review(file_content):
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
                You are a helpful assistant that reviews code and comments on a pull request.
                Please review the file patch from the github api:
                {file_content}

                Special Instruction:
                Pull request review thread line must be part of the diff, Pull request review thread start line must be part of the same hunk as the line, and Pull request review thread diff hunk can't be blank.

                The output must contain the following keys:
                body: The text of the review comment.
                line: The contents of the line where the change needs to be applied
                """,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[ReviewComment],
            },
        )
        return response.parsed
