�y1. �͂��߂Ɂz

���̃A�v���́A�������͂���OpenAI API����ăL�����N�^�[�u�C�ӂ̃L�����N�^�v�̎��R�ȉ����𐶐����A�����o�͂܂ł������������b�A�v���ł��B
VOICEVOX�̃��C�Z���X���̓��e�����邽�߁A���p���͂���C�͂���܂���

�쐬�����ړI�A���݃h�[���E�G��AI���g�p���ĉ�b���ł���@�B���������ꂽ���A�@�B�{�̂̒l�i��1��5��O��Ŗ���AI��1���߂��̓������K�v������
����ȍ����������o���Ďg�������Ȃ��̂ŁA�����Ŕ�r�I������OpenAI���g�p���Ď����悤�Ȃ��͍̂��Ȃ����ƍl���쐬����
PC��Bluetooth�@�\������}�C�N�ƃX�s�[�J�[�ƃ}�N���L�[�{�[�h������΂������Ő��\���ǂ�AI��b�c�[���Ƃ��Ďg�p�ł��邽�߁A
�R�[�h���܂߂Č��J���邱�Ƃɂ���B
�J�o������茫���l������Ƀc�[�������ǂ��Ďg���₷�����Ă����Ə�����I


�J�o�����l���Ă��鉓�u����ꎮ
�}�N���L�[�{�[�h�iAmazon�j
https://www.amazon.co.jp/dp/B0BCJZPHTK/?coliid=I1ZVCTNOS4XHWS&colid=1H2FRGB9MXPNI&ref_=list_c_wl_lv_ov_lig_dp_it&th=1
iPone���g�p�iSE2�j
�ڍׂ͊��\�z�菇�Ő���

�r�[�v�����̉����͉��LURL����]�p���Ă��܂�
https://soundeffect-lab.info/sound/button/


�y2. �K�v�ȃC���X�g�[���iPython 3.11�O��j�z
���A�v���N���ɕK�v�ȍ\�z���͊��\�z�菇.txt���Q�Ƃ��Ă�������



�y3. �e .py �t�@�C���̐����z
�t�@�C�����F�@�\�T�v
main.py                     �F�A�v���̋N��/�^��/��������/�����ǂݏグ�𓝊�
chat/gpt_client.py          �F OpenAI�ւ̃��N�G�X�g�Ɖ����擾�A����ۑ�����
chat/conversation_manager.py�F ��b���O�̕ۑ��E�܂Ƃߏ���
memory/vector_store.py      �F �x�N�g��DB�i�L���j�̊Ǘ��ƍX�V
recorder/speech_to_text.py  �F �������e�L�X�g�ɕϊ����^�╶�������s��
voice/voicevox_client.py    �F �ԓ��e�L�X�g��VOICEVOX�ŉ����ϊ����Đ�����
tool/*.py                   �F �}�C�N�̈ꗗ��C���f�b�N�X�擾�Ɏg�p



�y4. character_prompt.txt�z
config/character_prompt.txt �ɂăL�����ݒ�𐧌�B
���e�́u�ݒ肵���L�����v�Ƃ��ĐU�镑�����߂̃v�����v�g��`�B
���̃e�L�X�g��OpenAI�֓n����A�ԓ����u�ݒ肳�ꂽ�L�����v�炵���Ȃ�܂��B



�y5. ��b���O�̕ۑ��E�����̎d�g�݁z
���O���	����
outputs/conversation_log.json                �F �S�Ẳ�b�����i���[��/�����t���j
outputs/memory_logs/                         �F �L���p�r�ʂɉߋ��̉�b��ۑ��B
short_term.json/mid_term.json/long_term.json �F �Z���L���A�����L���A�����L����OpenAI�֘A�g����t�����
outputs/records/YYYYMMDD/                    �F ��������ϊ����ꂽ���̓e�L�X�g�i�ꎞ�t�@�C���j
outputs/responses/YYYYMMDD/                  �F OpenAI����̉����i�ꎞ�t�@�C���j

���݂� conversation_log.json �ɂ܂Ƃߕۑ�����邽�߁A
records/responses �͓ǂݏグ��ɍ폜����܂��B



�y6. App.config �e�萔�̐����z

# ========== ���ʐݒ� ==========
[GENERAL]
inputs_dir = outputs/inputs
responses_dir = outputs/responses
���ږ��F����
inputs_dir   �F�����F�����ꂽ�e�L�X�g�̈ꎞ�ۑ���i���g�p������j
responses_dir�FOpenAI�����̕ۑ���iVOICEVOX�ǂݏグ�Ɏg�p�j

[RECORDER]
mic_device_index = 2
���ږ��F����
mic_device_index �F �g�p����}�C�N�f�o�C�X�̃C���f�b�N�X�ԍ��i���O�Ɋm�F�K�{�j
                    �ڑ����Ă���}�C�N�����o�����X�g������c�[���Ǝg�p�}�C�N�̌��m�c�[����p�ӂ��Ă���̂������g�p��
                    �}�C�N�f�o�C�X�̃C���f�b�N�X�ԍ����擾����i.../project_root/tool/�t�H���_�́ulist_microphones.py�v�Ɓumic_device_index.py�v���g�p���邱��

[CHAT]
character_prompt_file = config/character_prompt.txt
model = gpt-4o-mini
api_key = sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
���ږ�:����
character_prompt_file�F �L�����N�^�[����ێ����邽�߂̃v�����v�g�t�@�C���p�X
model                �F �g�p����OpenAI���f���i��Fgpt-4o-mini�j
api_key              �F OpenAI��API�L�[�i�R�k���ӁI�j
                        OpenAI�Ƀ��O�C������o�^���AAPI_Key�𕥂��o���\��t���Ă��������B�擾���@�͕ʓr��������

[VOICEVOX]
host = 127.0.0.1
port = 50021
speaker_id = 1
���ږ�:����
host        �F VOICEVOX�T�[�o�[�̃z�X�g�A�h���X�i�ʏ�� 127.0.0.1�j
port        �F VOICEVOX�̃|�[�g�ԍ��i�f�t�H���g�� 50021�j
speaker_id  �F �g�p����b��ID�iVOICEVOX�őI�������L�����ɉ����ĕύX�j

[KEYS]
record_key = f9
exit_key = esc
���ږ��F����
record_key�F �^���J�n�L�[�i�f�t�H���g: F9�j
exit_key  �F �A�v���I���L�[�i�f�t�H���g: ESC�j

[MEMORY]
memory_level = 1
long_term_hits = 5
long_term_min_score = 0.3
mid_term_days = 3
���ږ��F����
memory_level       �F ��b�����̎g�p�͈͂�؂�ւ���(0=�L���Ȃ�, 1=�Z��, 2=����, 3=����)
long_term_hits     �F �ގ������b�����̌�������i��F�ߋ��̗ގ�������������o�����j
long_term_min_score�F �x�N�g���ގ��x��臒l�i0.0?1.0�j������Ⴂ�ƋL���Ƃ��č̗p���Ȃ�
mid_term_days      �F �u�����L���v�̑ΏۂƂȂ�����i��F3�Ȃ璼��3������v��Ŏ擾�j

[CONVERSATION]
question_suffixes = ��,����,�ł���,��,�Ȃ�,����,����,�̂���,�Ȃ��,����,�Ȃ�,�Ȃ���,�Ȃɂ���
���ږ��F����
question_suffixes�F �^�╄���Ō�ɕt��������̕�����B�����ŋL�ڂ���Ă��镶���񂪉�b�̍Ō���ɂ��Ă����ꍇ�^�╄��t����
