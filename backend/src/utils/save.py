# src/utils_save.py

def save_visualization(fig, output_file):
    '''
    図を画像ファイルとして保存
    '''
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"画像が {output_file} として保存されました。")
