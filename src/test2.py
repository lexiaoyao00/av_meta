from modules.analysis_file import AnalysisFile

if __name__ == '__main__':
    file_dir = 'F:/pikpakDownload'
    analysis_file = AnalysisFile(file_dir)
    file_list = analysis_file.get_video_path_list()
    success,failed,uncertain = analysis_file.extract_av_code(files=file_list)
    print(success)
    print(failed)
    print(uncertain)