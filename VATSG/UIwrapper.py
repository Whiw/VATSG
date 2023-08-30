class UIwrapper:
    def __init__(self, queue, lock, key, cuda_var, translateoption_var, srclanguagecodeinput, targetlanguagecodinput, original_var, fast_option):
        self.queue = queue
        self.lock = lock
        self.key = key
        self.cuda_var = cuda_var
        self.translateoption_var = translateoption_var
        self.srclanguagecodeinput = srclanguagecodeinput
        self.targetlanguagecodinput = targetlanguagecodinput
        self.original_var = original_var
        self.fast_option = fast_option

    def update_percentagelabel_post(self, text, value):
        with self.lock:
            self.queue.put((text, value))

    def update_progressbar(self, text, value):
        with self.lock:
            self.queue.put((text, value))

    def getkey(self):
        return self.key

    def get_progressbar(self):
        return self.progressbar

    def get_percentagelabel(self):
        return self.percentagelabel

    def get_cuda_var(self):
        return self.cuda_var

    def get_translateoption_Var(self):
        return self.translateoption_var

    def get_srclanguagecodeinput(self):
        return self.srclanguagecodeinput

    def get_trglanguagecodeinput(self):
        return self.targetlanguagecodinput

    def get_original_var(self):
        return self.original_var

    def get_fast_var(self):
        return self.fast_option
