import subprocess

def ptex2pdf(texfile:str,output_dir:str):
    subprocess.run('ptex2pdf %s -l -u -output-directory %s -ot "-synctex=1 -file-line-error -shell-escape"' % (texfile,output_dir), shell=True)
    # file_name = texfile.replace(".tex","")
    # delete_extensions = ["aux","log","synctex.gz"]
    # for e in delete_extensions:
    #     subprocess.run("rm %s.%s" % (file_name,e), shell=True)

def pdf2jpeg(pdffile:str,output_file:str):
    subprocess.run("convert -density 1920x1920 %s %s" % (pdffile,output_file), shell=True)