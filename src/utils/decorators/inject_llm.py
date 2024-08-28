# 装饰器定义
def inject_llm(llm_instance):
    def decorator(cls):
        cls.llm = llm_instance  # 注入 llm 实例到类中
        original_init = cls.__init__
        
        # 修改 __init__ 方法，在实例化时注入 llm 到实例
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.llm = llm_instance  # 注入 llm 实例到实例属性
        cls.__init__ = new_init
        
        return cls
    return decorator