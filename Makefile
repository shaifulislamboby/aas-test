start:
	docker compose up -d

push:
	git add . && git commit --amend --no-edit && git push --force-with-lease