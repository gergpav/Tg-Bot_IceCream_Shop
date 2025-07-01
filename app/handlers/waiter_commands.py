from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.deserializator import deserialize_callback_data


async def waiter_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat and update.effective_user:
        await context.application.user_service.register_visitor(update.effective_user.id)  # type: ignore[attr-defined, union-attr]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Добро пожаловать, официант!")


async def waiter_finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    order_service: OrderService = context.application.order_service  # type: ignore[attr-defined, union-attr]

    query = update.callback_query
    await query.answer()

    deserialized_callback_data = deserialize_callback_data(query.data)
    order_id = int(deserialized_callback_data[1])
    await order_service.mark_order_done(order_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Заказ был переведён в завершённые."
    )
    order = await order_service.get_order_by_id(order_id)
    user_id = order.user_id
    await context.bot.send_message(
        chat_id=user_id,
        text=f"Ваш заказ готов! Можете забирать."
    )

