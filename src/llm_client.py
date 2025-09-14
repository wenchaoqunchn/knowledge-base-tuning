"""
大模型API客户端模块
处理与大模型API的交互
"""

import requests
import re
from typing import List, Dict, Any, Optional
from .config import Config
from .utils import clean_content, mask


class LLMClient:
    """大模型API客户端"""

    def __init__(self, config: Config):
        self.config = config

    def chat(self, question: str, chat_id: str) -> str:
        """发送聊天请求"""
        url = self.config.url + "api/v1/chat/completions"
        headers = {
            "Authorization": "Bearer " + self.config.app.key,
            "Content-Type": "application/json",
        }
        data = {
            "chatId": chat_id,
            "stream": False,
            "detail": False,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": question}]}
            ],
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"请求成功, data:\n {data}")
            return clean_content(content)
        else:
            print(f"请求失败, 状态码: {response.status_code}")
            return ""

    def delete_one_chat(self, chat_id: str) -> Dict[str, Any]:
        """删除单个聊天记录"""
        url = self.config.url + "api/core/chat/delHistory"
        headers = {
            "Authorization": "Bearer " + self.config.app.key,
        }
        params = {"chatId": chat_id, "appId": self.config.app.id}

        response = requests.delete(url, headers=headers, params=params)

        if response.status_code == 200:
            print(f"删除成功, chat_id: {chat_id}")
        else:
            print(f"删除失败, 状态码: {response.status_code}")
        return response.json()

    def delete_all_chats(self) -> Dict[str, Any]:
        """删除所有聊天记录"""
        url = self.config.url + "api/core/chat/clearHistories"
        headers = {
            "Authorization": "Bearer " + self.config.app.key,
        }
        params = {"appId": self.config.app.id}

        response = requests.delete(url, headers=headers, params=params)

        if response.status_code == 200:
            print(
                f"所有聊天记录清除成功\n app_id = {mask(self.config.app.id)}\n app_key = {mask(self.config.app.key)}"
            )
        else:
            print(f"清除聊天记录失败, 状态码: {response.status_code}")
        return response.json()

    def delete_one_collection(self, collection_id: str) -> Dict[str, Any]:
        """删除单个集合"""
        url = self.config.url + "api/core/dataset/collection/delete"
        headers = {"Authorization": "Bearer " + self.config.dataset.key}
        params = {"id": collection_id}
        response = requests.delete(url, headers=headers, params=params)

        if response.status_code == 200:
            print(f"单个集合清除成功\n col_id = {collection_id}\n")
        else:
            print(f"清除单个集合失败, 状态码: {response.status_code}")
        return response.json()

    def get_collection_list(
        self, parent_id: Optional[str] = None, page: int = 0
    ) -> Dict[str, Any]:
        """获取集合列表"""
        url = self.config.url + "api/core/dataset/collection/listV2"
        headers = {
            "Authorization": "Bearer " + self.config.dataset.key,
            "Content-Type": "application/json",
        }
        data = {
            "offset": 30 * page,
            "pageSize": 30,
            "datasetId": self.config.dataset.id,
            "parentId": parent_id,
            "searchText": "",
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"成功获取集合列表")
        else:
            print(f"获取集合列表失败, 状态码: {response.status_code}")
        return response.json()

    def get_data_list(self, collection_id: str, page: int = 0) -> Dict[str, Any]:
        """获取数据列表"""
        url = self.config.url + "api/core/dataset/data/v2/list"
        headers = {
            "Authorization": "Bearer " + self.config.dataset.key,
            "Content-Type": "application/json",
        }
        data = {
            "offset": 30 * page,
            "pageSize": 30,
            "collectionId": collection_id,
            "searchText": "",
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"数据列表获取成功")
        else:
            print(f"获取数据列表失败, 状态码: {response.status_code}")
        return response.json()

    def add_index(
        self, data_id: str, data_q: str, index_list: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """添加索引"""
        url = self.config.url + "api/core/dataset/data/update"
        headers = {
            "Authorization": "Bearer " + self.config.dataset.key,
            "Content-Type": "application/json",
        }
        data = {"dataId": data_id, "q": data_q, "indexes": index_list}

        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"数据索引更新成功")
        else:
            print(f"索引更新失败, 状态码: {response.status_code}")
        return response.json()

    def process_table_with_llm(self, md_content: str, chat_id: str) -> str:
        """使用LLM处理表格内容"""
        self.delete_one_chat(chat_id)
        answer_list = []

        # 发送初始问题
        answer = self.chat(self.config.prompts.start_prompt + md_content, chat_id)
        answer_list.append(answer)

        # 继续对话直到结束
        while "<EOF>" not in answer:
            answer = self.chat(self.config.prompts.continue_prompt, chat_id)
            answer_list.append(answer)

        return "\n".join(answer_list)

    def generate_custom_indexes(
        self, content: str, data_id: str
    ) -> List[Dict[str, str]]:
        """生成自定义索引"""
        sum_prompt = """
你是一个制度条款关键词概括助手，请你充分理解我提供给你的条款段落，提取出索引列表，要求如下：1.提取出一组字符串列表。2.输出格式为[关键词1,关键词2,关键词3,可能的问题1,可能的问题2]，禁止输出其他无关内容。3.五个索引的提取思路各不相同，关键词1结合父级标题和段落正文内容为这个条款拟定一个具体的细化到当前条款的小标题，重点强调该条款在父级标题之下体现的独特规范作用侧重点；关键词2对段落正文规定的是什么进行一句话全面概括，尽量不要漏掉细节；关键词3提取出当前条款所适用的省市机构名称信息；问题1和问题2从不了解制度文档的员工视角进行提问，提出两个用户最有可能针对这个条款提出的两个长问题。以下是条款内容,请结合上述要求输出包含五个字符串索引的列表：\n
"""

        chat_id = data_id
        self.delete_one_chat(chat_id)
        ans = self.chat(sum_prompt + content, chat_id)

        # 解析回答中的索引
        return self._parse_index_response(ans)

    def _parse_index_response(self, ans: str) -> List[Dict[str, str]]:
        """解析索引回答"""
        try:
            # 提取方括号内的内容
            match = re.search(r"\[(.*?)\]", ans)
            if not match:
                return []

            content = match.group(1)
            items = [item.strip() for item in content.split(",")]

            # 构造目标格式
            return [{"type": "custom", "text": item} for item in items]
        except Exception as e:
            print(f"解析索引回答失败: {e}")
            return []
