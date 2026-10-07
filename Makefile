.PHONY: site clean serve

# src/docs/*.md -> docs/, then the marketing page copied over the top.
site: clean
	uv run --group dev mkdocs build --strict
	cp -R src/html/. docs/

clean:
	rm -rf docs

serve:
	uv run --group dev mkdocs serve
