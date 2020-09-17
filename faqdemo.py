from browser import aio
import chat

async def main(insertAfterID=None):
    'let student select FAQs to view or create a new FAQ'
    fms = chat.FaqMultiSelection("faq-list-template", insertAfterID=insertAfterID)
    faqs = await fms.get()
    insertAfterID = fms.insertAfterID
    for inquiry in faqs:
        insertAfterID = await show_faq(inquiry, faqs[inquiry], insertAfterID)
    anyFaqPrompt = chat.AnyQuestionsPrompt(insertAfterID=insertAfterID)
    hasQuestion = await anyFaqPrompt.get()
    insertAfterID = anyFaqPrompt.insertAfterID
    if hasQuestion == 'yes':
        insertAfterID = await create_new_faq(insertAfterID)
    chat.post_messages((("ChatMessageTemplate", "OK, let's continue."),), insertAfterID=insertAfterID)


async def show_faq(inquiry, answer, insertAfterID=None):
    'show full question and option to view answer'
    prompt = chat.FullFaqPrompt(inquiry, insertAfterID=insertAfterID)
    helpful = await prompt.get()
    insertAfterID = prompt.insertAfterID
    if helpful == 'yes' and answer:
        insertAfterID = await show_faq_answer(answer, insertAfterID)
    return insertAfterID

async def show_faq_answer(answer, insertAfterID=None):
    'show answer and ask status'
    prompt = chat.FaqStatusPrompt(answer, insertAfterID=insertAfterID)
    status = await prompt.get()
    insertAfterID = prompt.insertAfterID
    if status == 'help':
        lastID = chat.post_messages((("ChatMessageTemplate", "We will try to provide more explanation for this."),), insertAfterID=insertAfterID)
        if insertAfterID:
            insertAfterID = lastID
    return insertAfterID


async def create_new_faq(insertAfterID=None):
    'student writes a new FAQ question'
    prompt = chat.ChatInput((("ChatMessageTemplate", "First, write a 'headline version' of your question as a single sentence, as clearly and simply as you can. (You'll have a chance to explain your question fully in the next step)."),), insertAfterID=insertAfterID)
    title = await prompt.get()
    insertAfterID = prompt.insertAfterID
    prompt = chat.ChatInput((("ChatMessageTemplate", "Next, let's nail down exactly what you're unsure about, by applying your question to a real-world situation, to identify what specific outcome you're unsure about (e.g. 'is A going to happen, or B?')"),), insertAfterID=insertAfterID)
    text = await prompt.get()
    insertAfterID = prompt.insertAfterID
    lastID = chat.post_messages((("ChatMessageTemplate", "We'll try to get you an answer to this."),),
                                insertAfterID=insertAfterID)
    if insertAfterID:
        insertAfterID = lastID
    return insertAfterID





aio.run(main())

