## 简介
本项目实现了监听微信消息，实现微信聊天机器人的功能。    
核心技术采用的是拦截web微信版消息的方式，模拟Web微信发送Http请求和接收Http响应。    

## 注意事项
* wxpy的chats.py文件，增加了一个 in_names 的方法，部署的时候一定要注意
* 语音识别采用的百度的AipSpeech，准确率有点儿太低
* pydub进行声音获取，需要安装FFmpeg，FFmpeg必须安装opencore-amr插件
