from browser import document, aio

def copy_to_container(templateID, containerID, msgText=None, selector=None, handler=None, **kwargs):
    'clone a template, inject content, and append to container'
    template = document[templateID]
    message = template.cloneNode(True) # clone its full subtree including all descendants
    message.id = webfsm_id.next()
    if msgText:
        contentElement = message.select(selector)[0]
        contentElement.html = msgText
    if handler:
        bind_event(handler, message, selector, **kwargs)
    container = document[containerID]
    container <= message # append to container's children
    document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight # scroll to bottom
    return message, container

def post_messages(chats, chatContainer="chatSection", chatSelector='.chat-bubble'):
    'post one or more messages to the chat'
    for t, m in chats: # inject chat messages
        copy_to_container(t, chatContainer, m, chatSelector)


def set_visibility(targetID, visible=True):
    target = document[targetID]
    if visible:
        target.style = "display: block;"
    else:
        target.style = "display: none;"

def bind_event(func, d=document, selector='button[data-option-value]', event='click'):
    for button in d.select(selector):
        button.bind(event, func)

def generate_id(stemFormat='webfsm%d'):
    'generate unique IDs for webfsm DOM elements'
    i = 0
    while True:
        yield stemFormat % i
        i += 1

webfsm_id = generate_id() # get iterator

############################################################

class ChatQuery(object):
    'prompt user with chat messages, then await get() to receive button click'
    def __init__(self, chats, responseTemplate="chat-options-template", responseContainer="chat-input-container",
            dataAttr='data-option-value', selector='button[data-option-value]'):
        post_messages(chats)
        self.temporary = copy_to_container(responseTemplate, responseContainer, selector=selector, handler=self.handler)[0]
        self.outcome = self.message = None
        self.dataAttr = dataAttr
    def handler(self, ev):
        self.outcome = ev.target.attrs[self.dataAttr]
        self.message = ev.target.html
    async def get(self):
        while True:
            await aio.sleep(1)
            if self.outcome:
                self.close()
                return self.outcome
    def close(self):
        if self.message:
            post_messages((("StudentMessageTemplate", self.message),))
        if self.temporary:
            self.temporary.remove() # delete this element from the DOM


class ChatInput(ChatQuery):
    'prompt user with chat messages, then await get() to receive textarea'
    def __init__(self, chats, **kwargs):
        ChatQuery.__init__(self, chats, "chat-text-template", selector="button", **kwargs)
    def handler(self, ev):
        self.outcome = self.message = self.temporary.select("textarea")[0].value

class FaqMultiSelection(ChatQuery):
    'prompt user with chat messages, then await get() to receive multiple-selection'
    def __init__(self, faq="faq-list-template", **kwargs):
        chats = (("ChatMessageTemplate", "Would any of the following questions help you? Select the one(s) you wish to view."), (faq, None))
        ChatQuery.__init__(self, chats, "continue-template", selector="button", **kwargs)
    def handler(self, ev):
        self.outcome = {"faq-q1" : "faq-a1"}

class FullFaqPrompt(ChatQuery):
    'prompt user with full-length question, then await get() to receive yes vs. no button click'
    def __init__(self, inquiry, **kwargs):
        chats = ((inquiry, None), ("ChatMessageTemplate", "Would the answer to this question help you?"))
        ChatQuery.__init__(self, chats, "yesno-template", **kwargs)

class FaqStatusPrompt(ChatQuery):
    def __init__(self, answer, **kwargs):
        chats = ((answer, None), ("ChatMessageTemplate", "How well do you feel you understand now? If you need more clarification, tell us."))
        ChatQuery.__init__(self, chats, "status-options-template", **kwargs)

class AnyQuestionsPrompt(ChatQuery):
    def __init__(self, **kwargs):
        chats = (("ChatMessageTemplate", "Is there anything else you're wondering about, where you'd like clarification or something you're unsure about this point?"),)
        ChatQuery.__init__(self, chats, "yesno-template", **kwargs)


################################################################
# distinct states:
# * pose a question, get response from chat-input-text
# * show text message, wait to Continue
# * request a choice via multiple-choice buttons
# * request a selection via multiple-selection list
