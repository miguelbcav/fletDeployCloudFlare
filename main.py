import flet as ft
import aiohttp
import asyncio
import time

# Token de autenticação atualizado
TOKEN = "RytmH5pJHn6kAFQi2HRpSaGh0og8V0LW"
table_id = 338693
polling_interval = 10  # Intervalo de tempo em segundos para verificar atualizações

# Função assíncrona para buscar os dados de uma linha específica
async def fetch_movie_data(session, row_id):
    url = f"https://api.baserow.io/api/database/rows/table/{table_id}/{row_id}/?user_field_names=true"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            nome = data.get('Nome', '')
            capa = data.get('Capa', '')
            video_link = data.get('Link', '')
            sinopse = data.get('Sinopse', '')
            return nome, capa, video_link, sinopse
        else:
            return "", "", "", ""

# Função para carregar os filmes e vídeos de forma assíncrona
async def load_movies():
    movies = []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, 803):  # Ajuste o intervalo conforme necessário
            task = asyncio.ensure_future(fetch_movie_data(session, i))
            tasks.append(task)
        movies_data = await asyncio.gather(*tasks)

    for nome, capa, video_link, sinopse in movies_data:
        if nome and capa and video_link:
            movies.append((nome, capa, video_link, sinopse))
    
    return movies

def main(page: ft.Page):
    page.theme_mode = "dark"
    page.padding = 0
    page.title = "MovieX"

    movie_controls = ft.Row(spacing=10, wrap=True, scroll="auto")

    async def update_movies():
        while True:
            movies = await load_movies()
            movie_controls.controls.clear()
            movie_controls.controls.extend(
                create_movie_card(movie[0], movie[1], movie[2], movie[3]) for movie in movies
            )
            page.update()
            await asyncio.sleep(polling_interval)

    def navigate_to_video_page(movie_name, video_playlist, sinopse):
        def go_back(e):
            page.views.pop()
            page.go(page.views[-1].route)

        video_page = ft.View(
            route="/video",
            controls=[
                ft.AppBar(
                    title=ft.Text(movie_name, weight="bold"),
                    leading=ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=go_back,
                    ),
                    bgcolor="#2A2A48",
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        scroll="auto",
                        horizontal_alignment="center",
                        controls=[
                            ft.Video(
                                title=movie_name,
                                playlist=video_playlist,
                                fit=ft.ImageFit.COVER,
                                playlist_mode=ft.PlaylistMode.LOOP,
                                fill_color=ft.colors.BLACK87,
                                aspect_ratio=16/9,
                                volume=100,
                                autoplay=True,
                                filter_quality=ft.FilterQuality.HIGH,
                                muted=False,
                                on_loaded=lambda e: print("Video loaded successfully!"),
                                on_enter_fullscreen=lambda e: print("Video entered fullscreen!"),
                                on_exit_fullscreen=lambda e: print("Video exited fullscreen!"),
                            ),
                            ft.Text(movie_name, size=32, color="White", text_align="center", weight="bold"),
                            ft.Divider(color="grey"),
                            ft.Container(
                                content=ft.Row(
                                    wrap=True,
                                    controls=[
                                        ft.Text("Sinopse: ", color="white", weight="w600", text_align="center"),
                                        ft.Text(value=f"{sinopse}", no_wrap=False, color="White")
                                    ]
                                )
                            )
                        ]
                    )
                ),
            ]
        )
        page.views.append(video_page)
        page.go("/video")

    def create_movie_card(movie_name, image_url, video_link, sinopse):
        video_playlist = [ft.VideoMedia(resource=video_link, extras={image_url: "https://image.tmdb.org/t/p/w185/w05T2c3jLhLCHa0lFMuxH4kDwua.jpg"})]
        return ft.Container(
            content=ft.Column(
                [
                    ft.Image(src=image_url, fit="contain", width=150, height=200, border_radius=20),
                    ft.Text(movie_name, text_align=ft.TextAlign.CENTER, width=160, height=50, max_lines=2, color="white", weight="w600"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            ),
            width=155,
            height=260,
            padding=10,
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.all(20),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=['#2A2A48', "#3e3e63", "#4e4e78"]
            ),
            on_click=lambda e: navigate_to_video_page(movie_name, video_playlist, sinopse)
        )

    page.add(
        ft.Container(
            expand=True,
            padding=20,
            bgcolor="#1f1f36",
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Text("Filmes", color="white", weight="bold", size=25, font_family="MontSerrat"),
                    movie_controls,
                ],
                scroll="auto"
            ),
        )
    )

    asyncio.run(update_movies())

if __name__ == '__main__':
    ft.app(target=main, assets_dir="assets",view=ft.AppView.WEB_BROWSER)
