from browser import aio
import chat

async def main(insertBeforeID=None):
    'basic ORCT chat cycle, starting with a simple updates test'
    await offer_updates(update_test, 'TestAfterPoint')
    s = await pose_orct(insertBeforeID)
    if s != 'same':
        await offer_errmods(insertBeforeID)
        await offer_faqs(insertBeforeID)
    await chat.continue_button((("ChatMessageTemplate", "Now you can move to the next lesson"),),
                       insertBeforeID=insertBeforeID)


async def pose_orct(insertBeforeID=None):
    'ask question, student responds, self-evaluates answer'
    chat.post_messages((("ChatBreakpointTemplate", "Efficiency Concerns: When to Include an ORCT?"),),
                       chatSelector='span', insertBeforeID=insertBeforeID)
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


async def create_new_faq(insertBeforeID=None, messageStamp=''):
    'student writes a new FAQ question'
    title = await chat.query((("ChatMessageTemplate", f"First, write a 'headline version' of your question as a single sentence, as clearly and simply as you can. (You'll have a chance to explain your question fully in the next step). {messageStamp}"),), insertBeforeID=insertBeforeID, klass=chat.ChatInput)
    text = await chat.query((("ChatMessageTemplate", f"Next, let's nail down exactly what you're unsure about, by applying your question to a real-world situation, to identify what specific outcome you're unsure about (e.g. 'is A going to happen, or B?') {messageStamp}"),), insertBeforeID=insertBeforeID, klass=chat.ChatInput)
    chat.post_messages((("ChatMessageTemplate", f"We'll try to get you an answer to this. {messageStamp}"),),
                       insertBeforeID=insertBeforeID)



async def offer_updates(updateFunc, insertBeforeID, **kwargs):
    'let student view or skip display of updates'
    wantUpdates = await chat.query((("ChatMessageTemplate", '''You have completed this thread. I have posted new messages to help you in the thread "Active Learning Approaches for Conceptual Understanding?". Would you like to view these updates now?<BR><BR><i>If you don't want to view them now, I'll ask you again once you have completed your next thread.</i>'''),),
                        'yesno-template')
    if wantUpdates != 'yes':
        return
    toggler = chat.HistoryToggle(insertBeforeID)
    await updateFunc(insertBeforeID, **kwargs)
    toggler.close()


async def update_test(insertBeforeID):
    'a trivial test of display a simple'
    await chat.continue_button((("ChatMessageTemplate", 'There are new answers for FAQs you are interested in <span class="chat-new-msg">new</span>'), ("ChatMessageTemplate", '<b>Please, Professor, can you explain exactly what I am confused about?</b><br>I am a student who is very confused, and am hoping that you can make everything clear to me. <span class="chat-new-msg">new</span>'),),
                       insertBeforeID=insertBeforeID)
    await chat.continue_button((("ChatMessageTemplate", 'I, the instructor, am now answering your question in great detail: yada yada yada. <span class="chat-new-msg">new</span>'),),
                       insertBeforeID=insertBeforeID)
    hasQuestion = await chat.query((("ChatMessageTemplate", 'Have you anything else you are worried about? <span class="chat-new-msg">new</span>'),),
                        'yesno-template', insertBeforeID=insertBeforeID)
    if hasQuestion == 'yes':
        await create_new_faq(insertBeforeID, messageStamp='<span class="chat-new-msg">new</span>')
    await chat.continue_button((("ChatMessageTemplate", 'You have completed this thread. Click on Continue below to view your next thread "Efficiency Concerns: When to Include an ORCT?". <span class="chat-new-msg">new</span>'),),
                       insertBeforeID=insertBeforeID)


aio.run(main())

