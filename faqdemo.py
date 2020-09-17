from browser import aio
import chat

async def main(insertBeforeID=None):
    'basic ORCT chat cycle, starting with a simple updates test'
    await offer_updates(update_test, 'TestAfterPoint')
    s = await pose_orct(insertBeforeID)
    if s != 'same':
        await offer_errmods(insertBeforeID)
        await offer_faqs(insertBeforeID)
    await chat.query((("ChatMessageTemplate", "Now you can move to the next lesson"),),
                       'continue-template', insertBeforeID=insertBeforeID)


async def pose_orct(insertBeforeID=None):
    'ask question, student responds, self-evaluates answer'
    await chat.query((("ChatMessageTemplate", "What is the airspeed of a fully laden swallow?"),),
                    insertBeforeID=insertBeforeID, klass=chat.ChatInput)
    await chat.query((("ChatMessageTemplate", None),),
                       'chat-options-template', insertBeforeID=insertBeforeID)
    return await chat.query((("ChatMessageTemplate", 'A swallow flies 40 km/h'), ("ChatMessageTemplate", 'How close was your answer to the one shown here? '),),
                             'selfeval-options-template', insertBeforeID=insertBeforeID)




async def offer_errmods(insertBeforeID=None):
    'let student select Error Models to view'
    ems = await chat.query((("ChatMessageTemplate", "Here are the most common blindspots people reported when comparing their answer vs. the correct answer. Check the box(es) that seem relevant to your answer (if any)."), ("em-list-template", None)), insertBeforeID=insertBeforeID,
                            klass=chat.MultiSelection)
    for em in ems:
        await show_em(em, insertBeforeID)
    chat.post_messages((("ChatMessageTemplate", "OK, let's continue."),),
                       insertBeforeID=insertBeforeID)


async def show_em(em, insertBeforeID=None):
    'show error model and get student status'
    status = await chat.query(((em, None), ("ChatMessageTemplate", "Hope you've overcame the misconception"), ("ChatMessageTemplate", "How well do you feel you understand this blindspot now? If you need more clarifications, tell us.")), 'status-options-template', insertBeforeID=insertBeforeID)
    if status == 'help':
        chat.post_messages((("ChatMessageTemplate", "We will try to provide more explanation for this."),), insertBeforeID=insertBeforeID)



async def offer_faqs(insertBeforeID=None):
    'let student select FAQs to view or create a new FAQ'
    faqs = await chat.query((("ChatMessageTemplate", "Would any of the following questions help you? Select the one(s) you wish to view."), ("faq-list-template", None)), insertBeforeID=insertBeforeID,
                            klass=chat.MultiSelection)
    for inquiry in faqs:
        await show_faq(inquiry, faqs[inquiry], insertBeforeID)
    hasQuestion = await chat.query((("ChatMessageTemplate", "Is there anything else you're wondering about, where you'd like clarification or something you're unsure about this point?"),),
                        'yesno-template', insertBeforeID=insertBeforeID)
    if hasQuestion == 'yes':
        await create_new_faq(insertBeforeID)
    chat.post_messages((("ChatMessageTemplate", "OK, let's continue."),),
                       insertBeforeID=insertBeforeID)


async def show_faq(inquiry, answer, insertBeforeID=None):
    'show full question and option to view answer'
    helpful = await chat.query(((inquiry, None), ("ChatMessageTemplate", "Would the answer to this question help you?")), 'yesno-template', insertBeforeID=insertBeforeID)
    if helpful == 'yes' and answer:
        await show_faq_answer(answer, insertBeforeID)


async def show_faq_answer(answer, insertBeforeID=None):
    'show answer and ask status'
    status = await chat.query(((answer, None), ("ChatMessageTemplate", "How well do you feel you understand now? If you need more clarification, tell us.")),
                            "status-options-template", insertBeforeID=insertBeforeID)
    if status == 'help':
        chat.post_messages((("ChatMessageTemplate", "We will try to provide more explanation for this."),), insertBeforeID=insertBeforeID)


async def create_new_faq(insertBeforeID=None):
    'student writes a new FAQ question'
    title = await chat.query((("ChatMessageTemplate", "First, write a 'headline version' of your question as a single sentence, as clearly and simply as you can. (You'll have a chance to explain your question fully in the next step)."),), insertBeforeID=insertBeforeID, klass=chat.ChatInput)
    text = await chat.query((("ChatMessageTemplate", "Next, let's nail down exactly what you're unsure about, by applying your question to a real-world situation, to identify what specific outcome you're unsure about (e.g. 'is A going to happen, or B?')"),), insertBeforeID=insertBeforeID, klass=chat.ChatInput)
    chat.post_messages((("ChatMessageTemplate", "We'll try to get you an answer to this."),),
                       insertBeforeID=insertBeforeID)



async def offer_updates(updateFunc, insertBeforeID, **kwargs):
    'let student view or skip display of updates'
    wantUpdates = await chat.query((("ChatMessageTemplate", 'Updates are available for "This Question".  Do you want to view the updates now?'),),
                        'yesno-template')
    if wantUpdates != 'yes':
        return
    toggler = chat.HistoryToggle(insertBeforeID)
    await updateFunc(insertBeforeID, **kwargs)
    toggler.close()


async def update_test(insertBeforeID):
    'a trivial test of display a simple'
    like = await chat.query((("ChatMessageTemplate", 'Here is a nice update.  Do you like it? <span class="chat-new-msg">new</span>'),),
                        'yesno-template', insertBeforeID=insertBeforeID)


aio.run(main())

