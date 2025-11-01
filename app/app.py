import reflex as rx
from app.state import AppState


def metric_card(icon: str, label: str, value: rx.Var[str]) -> rx.Component:
    """A card for displaying a single metric."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-gray-400"),
            class_name="p-3 bg-gray-100 rounded-full mb-4",
        ),
        rx.el.p(label, class_name="text-sm font-medium text-gray-500 mb-1"),
        rx.el.p(value, class_name="text-2xl font-semibold text-gray-800"),
        class_name="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-lg hover:border-orange-200 transition-all duration-300",
        style={"box-shadow": "0px 1px 3px rgba(0,0,0,0.12)"},
    )


def profile_header(profile: rx.Var[dict]) -> rx.Component:
    """Displays the main profile information."""
    return rx.el.div(
        rx.image(
            src=profile["profile_pic_url"],
            class_name="h-24 w-24 rounded-full border-4 border-white shadow-md",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    profile["username"], class_name="text-2xl font-bold text-gray-900"
                ),
                rx.icon("badge-check", class_name="h-6 w-6 text-orange-500"),
            ),
            rx.el.p(
                profile["bio"], class_name="text-gray-600 mt-2 text-center max-w-lg"
            ),
            class_name="flex flex-col items-center ml-6",
        ),
        class_name="flex items-center",
    )


def analysis_dashboard() -> rx.Component:
    """The main component to display after a successful search."""
    return rx.el.div(
        profile_header(AppState.profile_data),
        rx.el.div(
            metric_card("users", "Followers", AppState.profile_data["followers"]),
            metric_card("user-plus", "Following", AppState.profile_data["following"]),
            metric_card(
                "pencil-ruler",
                "Total Posts",
                AppState.profile_data["posts"].to_string(),
            ),
            metric_card(
                "activity",
                "Engagement Rate",
                AppState.profile_data["engagement_rate"].to_string() + "%",
            ),
            class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mt-8 w-full",
        ),
        rx.el.div(
            engagement_chart_card(),
            recent_posts_gallery(),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6 w-full",
        ),
        class_name="flex flex-col items-center justify-center p-8 bg-gray-50 rounded-2xl mt-8 border border-gray-200 w-full",
        style={"box-shadow": "0px 3px 6px rgba(0,0,0,0.1)"},
    )


def search_section() -> rx.Component:
    """The search input and button component."""
    return rx.el.div(
        rx.el.h1(
            "Instagram Profile Analyzer",
            class_name="text-3xl md:text-4xl font-bold text-gray-800",
        ),
        rx.el.p(
            "Get key insights on any public Instagram profile.",
            class_name="text-gray-500 mt-2 mb-8",
        ),
        rx.el.form(
            rx.el.div(
                rx.icon(
                    "at-sign",
                    class_name="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400",
                ),
                rx.el.input(
                    placeholder="Enter Instagram username...",
                    name="username",
                    class_name="w-full pl-12 pr-4 py-4 text-lg bg-white border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-400 focus:border-orange-400 transition-all duration-300",
                    style={"box-shadow": "0px 1px 3px rgba(0,0,0,0.08)"},
                ),
                class_name="relative w-full max-w-lg",
            ),
            rx.el.button(
                "Analyze",
                rx.icon("search", class_name="ml-2"),
                type="submit",
                class_name="px-8 py-4 bg-orange-500 text-white font-semibold rounded-xl hover:bg-orange-600 transition-all duration-300 flex items-center",
                style={"box-shadow": "0px 4px 8px rgba(0,0,0,0.15)"},
            ),
            on_submit=AppState.handle_search,
            reset_on_submit=True,
            class_name="flex items-center gap-4",
        ),
        class_name="flex flex-col items-center text-center",
    )


def loading_skeleton() -> rx.Component:
    """A loading skeleton UI to show while fetching data."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(class_name="h-24 w-24 rounded-full bg-gray-200"),
            rx.el.div(
                rx.el.div(class_name="h-8 w-48 bg-gray-200 rounded-md"),
                rx.el.div(class_name="h-4 w-80 bg-gray-200 rounded-md mt-4"),
                class_name="flex flex-col items-center ml-6",
            ),
            class_name="flex items-center",
        ),
        rx.el.div(
            rx.el.div(class_name="h-36 bg-gray-200 rounded-2xl"),
            rx.el.div(class_name="h-36 bg-gray-200 rounded-2xl"),
            rx.el.div(class_name="h-36 bg-gray-200 rounded-2xl"),
            rx.el.div(class_name="h-36 bg-gray-200 rounded-2xl"),
            class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mt-8 w-full",
        ),
        class_name="flex flex-col items-center justify-center p-8 bg-gray-50 rounded-2xl mt-8 border border-gray-200 w-full animate-pulse",
    )


def error_display() -> rx.Component:
    """Displays an error message."""
    return rx.el.div(
        rx.icon("flag_triangle_right", class_name="h-12 w-12 text-red-400 mb-4"),
        rx.el.h3("Analysis Failed", class_name="text-xl font-semibold text-red-800"),
        rx.el.p(AppState.error_message, class_name="text-red-600 mt-2"),
        class_name="flex flex-col items-center p-8 bg-red-50 border border-red-200 rounded-2xl mt-8",
    )


def engagement_chart_card() -> rx.Component:
    """Card containing the engagement chart."""
    return rx.el.div(
        rx.el.h3(
            "Recent Engagement", class_name="text-lg font-semibold text-gray-800 mb-4"
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=True, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(cursor={"fill": "rgba(249, 115, 22, 0.1)"}),
            rx.recharts.x_axis(data_key="name", class_name="text-xs"),
            rx.recharts.y_axis(class_name="text-xs"),
            rx.recharts.bar(
                data_key="likes", fill="#F97316", name="Likes", radius=[4, 4, 0, 0]
            ),
            rx.recharts.bar(
                data_key="comments",
                fill="#FB923C",
                name="Comments",
                radius=[4, 4, 0, 0],
            ),
            data=AppState.profile_data["engagement_data"],
            height=300,
            class_name="w-full",
        ),
        class_name="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm col-span-1 lg:col-span-2",
    )


def post_card(post: rx.Var[dict]) -> rx.Component:
    """A card for a single Instagram post."""
    return rx.el.a(
        rx.image(
            src=post["display_url"], class_name="w-full h-32 object-cover rounded-t-xl"
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("heart", class_name="h-4 w-4 text-gray-500"),
                rx.el.p(post["likes"].to_string(), class_name="text-sm text-gray-600"),
                class_name="flex items-center gap-1",
            ),
            rx.el.div(
                rx.icon("message-circle", class_name="h-4 w-4 text-gray-500"),
                rx.el.p(
                    post["comments"].to_string(), class_name="text-sm text-gray-600"
                ),
                class_name="flex items-center gap-1",
            ),
            class_name="flex justify-between p-3 bg-gray-50 rounded-b-xl border-t border-gray-200",
        ),
        href=f"https://instagram.com/p/{post['shortcode']}",
        is_external=True,
        class_name="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-lg transition-shadow duration-300 overflow-hidden block",
    )


def recent_posts_gallery() -> rx.Component:
    """A gallery of recent Instagram posts."""
    return rx.el.div(
        rx.el.h3("Recent Posts", class_name="text-lg font-semibold text-gray-800 mb-4"),
        rx.el.div(
            rx.foreach(AppState.profile_data["recent_posts"], post_card),
            class_name="grid grid-cols-2 sm:grid-cols-3 gap-3",
        ),
        class_name="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.icon("bar-chart-3", class_name="h-8 w-8 text-orange-500"),
                rx.el.p(
                    "Influencer Analyzer", class_name="font-bold text-lg text-gray-700"
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="absolute top-6 left-6",
        ),
        rx.el.div(
            search_section(),
            rx.cond(
                AppState.is_loading,
                loading_skeleton(),
                rx.cond(
                    AppState.error_message,
                    error_display(),
                    rx.cond(AppState.profile_data, analysis_dashboard(), rx.el.div()),
                ),
            ),
            class_name="container mx-auto px-4 py-8 flex flex-col items-center w-full max-w-5xl",
        ),
        class_name="font-['Poppins'] bg-gray-50 min-h-screen relative flex justify-center items-start pt-24",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)