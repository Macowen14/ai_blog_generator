def wrap_blog_with_tailwind(html_content):
    return (
        f'<div class="max-w-3xl mx-auto p-4 prose prose-indigo">'
        f'{html_content}'
        f'</div>'
    )
