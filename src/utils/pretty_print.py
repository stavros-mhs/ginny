import shutil

def beautify (text: str = "", padding: str = "="):
    width = shutil.get_terminal_size().columns

    if not text:
        print (padding * width)
        return
    
    centered = f" {text.strip ()} "
    print (centered.center (width, padding))