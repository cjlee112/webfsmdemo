from browser import aio
import chat

async def main():
    'let student select FAQs to view or create a new FAQ'
    fms = chat.FaqMultiSelection("faq-list-template")
    faqs = await fms.get()
    for inquiry in faqs:
        await show_faq(inquiry, faqs[inquiry])
    anyFaqPrompt = chat.AnyQuestionsPrompt()
    hasQuestion = await anyFaqPrompt.get()
    if hasQuestion == 'yes':
        await create_new_faq()
    chat.post_messages((("ChatMessageTemplate", "OK, let's continue."),))


async def show_faq(inquiry, answer):
    'show full question and option to view answer'
    prompt = chat.FullFaqPrompt(inquiry)
    helpful = await prompt.get()
    if helpful == 'yes' and answer:
        await show_faq_answer(answer)


async def show_faq_answer(answer):
    'show answer and ask status'
    prompt = chat.FaqStatusPrompt(answer)
    status = await prompt.get()
    if status == 'help':
        chat.post_messages((("ChatMessageTemplate", "We will try to provide more explanation for this."),))


async def create_new_faq():
    'student writes a new FAQ question'
    prompt = chat.ChatInput((("ChatMessageTemplate", "First, write a 'headline version' of your question as a single sentence, as clearly and simply as you can. (You'll have a chance to explain your question fully in the next step)."),))
    title = await prompt.get()
    prompt = chat.ChatInput((("ChatMessageTemplate", "Next, let's nail down exactly what you're unsure about, by applying your question to a real-world situation, to identify what specific outcome you're unsure about (e.g. 'is A going to happen, or B?')"),))
    text = await prompt.get()
    chat.post_messages((("ChatMessageTemplate", "We'll try to get you an answer to this."),))





aio.run(main())

