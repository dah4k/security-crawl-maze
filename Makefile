all:
	docker build --tag crawlmaze .

test:
	docker run --rm --publish 8080:8080 --name crawlmaze crawlmaze

clean:
	docker rmi crawlmaze

distclean:
	docker image prune --force
	docker system prune --force

.PHONY: all test clean distclean
