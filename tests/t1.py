from io import StringIO
import logging
# 创建一个日志记录器
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
# 创建一个输出到字符串的处理器
output = StringIO()
handler = logging.StreamHandler(output)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
# 执行需要获取输出的代码
logger.debug('Hello, World!')
logger.info('123')
# 获取控制台输出的内容
output_text = output.getvalue()
print(output_text)