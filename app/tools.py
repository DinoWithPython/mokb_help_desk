"""Дополнительные функции для оптимизации кода."""
from app import db
from flask import current_app, url_for


def paginate_tool(data, page: int, url: str, name: str) -> {dict, dict, dict}:
    """Оптимизация пагинаторов."""
    data_pag = db.paginate(data, page=page,
                           per_page=current_app.config['POSTS_PER_PAGE'],
                           error_out=False)
    next_url = url_for(
        url, page=data_pag.next_num
        ) if data_pag.has_next else None
    prev_url = url_for(
        url, page=data_pag.prev_num
        ) if data_pag.has_prev else None
    return {
        name: data_pag,
        'next_url': next_url,
        'prev_url': prev_url
    }
