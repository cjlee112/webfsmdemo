from browser import document, aio

def copy_to_container(templateID, containerID, msgText=None, selector=None, handler=None, 
                      insertBeforeID=None, **kwargs):
    'clone a template, inject content, and append to container'
    template = document[templateID]
    message = template.cloneNode(True) # clone its full subtree including all descendants
    message.id = webfsm_id.__next__()
    if msgText:
        contentElement = message.select(selector)[0]
        contentElement.html = msgText
    if handler:
        bind_event(handler, message, selector, **kwargs)
    container = document[containerID]
    if insertBeforeID: # insert at this specific location
        container.insertBefore(message, document[insertBeforeID])
    else:
        container <= message # append to container's children
    document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight # scroll to bottom
    return message, container

def post_messages(chats, chatContainer="chatSection", chatSelector='.chat-bubble',
                    insertBeforeID=None):
    'post one or more messages to the chat'
    for t, m in chats: # inject chat messages
        copy_to_container(t, chatContainer, m, chatSelector, insertBeforeID=insertBeforeID)


def set_visibility(targetID, visible=True, displayStyle='block'):
    'show or hide a specific DOM container'
    target = document[targetID]
    if visible:
        target.style.display = displayStyle
    else:
        target.style.display = 'none'

def bind_event(func, d=document, selector='button[data-option-value]', event='click'):
    for button in d.select(selector):
        button.bind(event, func)

def generate_id(stemFormat='webfsm%d'):
    'generate unique IDs for webfsm DOM elements'
    i = 1
    while True:
        yield stemFormat % (i,)
        i += 1

webfsm_id = generate_id() # get iterator

############################################################

class ChatQuery(object):
    'prompt user with chat messages, then await get() to receive button click'
    def __init__(self, chats, responseTemplate="chat-options-template", responseContainer="chat-input-container",
            dataAttr='data-option-value', selector='button[data-option-value]',
            insertBeforeID=None):
        self.insertBeforeID = insertBeforeID
        post_messages(chats, insertBeforeID=insertBeforeID)
        self.temporary = copy_to_container(responseTemplate, responseContainer, selector=selector,
                                            handler=self.handler)[0]
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
            post_messages((("StudentMessageTemplate", self.message),),
                          insertBeforeID=self.insertBeforeID)
        if self.temporary:
            self.temporary.remove() # delete this element from the DOM


async def query(chats, *args, **kwargs):
    'perform query and return student response'
    try:
        klass = kwargs['klass']
        del kwargs['klass']
    except KeyError:
        klass = ChatQuery
    prompt = klass(chats, *args, **kwargs)
    return await prompt.get()

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


class HistoryToggle(object):
    def __init__(self, insertBeforeID, updateFlagger='UpdateFlagger', updateToggler='UpdateToggler'):
        self.target = document[insertBeforeID]
        self.controller = document[updateFlagger]
        self.msgToggler = document[updateToggler]
        set_visibility(updateFlagger)
        self.set_toggle()
        bind_event(self.handler, selector='#' + updateToggler)
    def handler(self, ev):
        self.set_toggle(not self.visible)
    def set_toggle(self, visible=False):
        if visible:
            self.msgToggler.text = '↑ Hide Subsequent Threads'
            self.target.scrollIntoView({'block': "center"})
            #document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight # scroll to bottom
        else:
            self.msgToggler.text = '↓ Show Subsequent Threads'
        self.visible = visible
        container = self.target.parent
        toggle = False
        for c in container.children:
            if c.id == self.target.id:
                toggle = True
            if toggle:
                set_visibility(c.id, visible)
    def close(self):
        set_visibility(self.controller.id, False)
        self.set_toggle(True)



################################################################
# distinct states:
# * pose a question, get response from chat-input-text
# * show text message, wait to Continue
# * request a choice via multiple-choice buttons
# * request a selection via multiple-selection list
