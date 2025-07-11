from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.core.orders.constants import OrderStatusEnum
from app.core.orders.exceptions import ActiveOrderExists
from app.core.orders.services import OrderService, ProductService
from app.handlers.helpers import build_order_buttons, format_order_contents, format_order_contents_for_waiter
from app.handlers.deserializator import deserialize_callback_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat and update.effective_user:
        await context.application.user_service.register_visitor(update.effective_user.id)  # type: ignore[attr-defined, union-attr]
        keyboard = [
            [InlineKeyboardButton("Сделать заказ", callback_data="create_order")],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Добро пожаловать!",
                                       reply_markup=markup)


async def create_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    order_service: OrderService = context.application.order_service  # type: ignore[attr-defined, union-attr]
    product_service: ProductService = context.application.product_service  # type: ignore[attr-defined, union-attr]

    try:
        order_id = await order_service.create_order(update.effective_user.id)
        items = await product_service.list_products()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Добавьте блюдо или напиток в заказ",
            reply_markup=build_order_buttons(order_id, items)
        )
    except ActiveOrderExists:
        active_order = await order_service.get_active_order_for_user(
            user_id=update.effective_user.id
        )
        if active_order.status == OrderStatusEnum.ordered:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"У вас уже есть предыдущий заказ, дождитесь его завершения.\n"
                     f"Предыдущий заказ: <b>{active_order.id}</b>\n\n"
                     f"{format_order_contents(active_order)}",
                parse_mode=ParseMode.HTML
            )
        elif active_order.status == OrderStatusEnum.unlisted:
            items = await context.application.product_service.list_products()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=format_order_contents(active_order),
                reply_markup=build_order_buttons(active_order.id, items),
                parse_mode=ParseMode.HTML
            )


async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    deserialized_callback_data = deserialize_callback_data(query.data)

    order_service: OrderService = context.application.order_service  # type: ignore[attr-defined, union-attr]
    product_service: ProductService = context.application.product_service  # type: ignore[attr-defined, union-attr]

    if deserialized_callback_data[1] == "None" or deserialized_callback_data[2] == "None":
        # обработка ошибки или return
        return

    order_id, item_id = int(deserialized_callback_data[1]), int(deserialized_callback_data[2])
    products = await product_service.list_products()

    await order_service.add_product_to_order(order_id, item_id)
    order = await order_service.get_order_by_id(order_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=format_order_contents(order),
        reply_markup=build_order_buttons(order_id, products),
        parse_mode=ParseMode.HTML
    )


async def finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    deserialized_callback_data = deserialize_callback_data(query.data)

    order_service: OrderService = context.application.order_service  # type: ignore[attr-defined, union-attr]
    user_service: UserService = context.application.user_service  # type: ignore[attr-defined, union-attr]

    order_id = int(deserialized_callback_data[1])
    await order_service.send_order_to_waiters(order_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ваш заказ передан официантам. Ожидайте, пожалуйста.",
    )
    waiter_users_ids = await user_service.get_waiter_user_ids()
    order = await order_service.get_order_by_id(order_id)

    for waiter_user_id in waiter_users_ids:
        await context.bot.send_message(
            chat_id=waiter_user_id,
            text=f"Создан новый заказ: {order_id}\n\n"
                 f"{format_order_contents_for_waiter(order)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Заказ доставлен", callback_data=f"waiter_finish_order|{order_id}")]
            ]),
            parse_mode=ParseMode.HTML
        )




