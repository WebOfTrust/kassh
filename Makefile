.PHONY: build-kassh
build-kassh:
	@docker buildx build --platform=linux/amd64 --no-cache -f containers/kassh.dockerfile --tag gleif/kassh:latest --tag gleif/kassh:0.1.0 .

.PHONY: run-kassh
run-agent:
	@docker run -p 5921:5921 -p 5923:5923 --name agent gleif/kassh:0.1.0

.PHONY: push-all
push-all:
	@docker push gleif/kassh --all-tags
