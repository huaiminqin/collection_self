"""
属性测试 - 使用Hypothesis进行属性测试
"""
import pytest
from hypothesis import given, strategies as st, settings as hypothesis_settings
from sqlalchemy.orm import Session

from app.models import College, Grade, Class, Member, Task, Submission


# 配置Hypothesis运行至少100次迭代
hypothesis_settings.register_profile("ci", max_examples=100)
hypothesis_settings.load_profile("ci")


# ============ Property 1: 组织结构创建一致性 ============
# **Feature: class-file-collection, Property 1: 组织结构创建一致性**
# **Validates: Requirements 1.1, 1.2, 1.3**

@given(
    college_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
)
def test_college_creation_consistency(db_session: Session, college_name: str):
    """
    **Feature: class-file-collection, Property 1: 组织结构创建一致性**
    对于任意学院名称，创建后该实体应出现在对应的列表中。
    """
    # 创建学院
    college = College(name=college_name)
    db_session.add(college)
    db_session.commit()
    db_session.refresh(college)
    
    # 验证学院存在于列表中
    colleges = db_session.query(College).all()
    college_names = [c.name for c in colleges]
    assert college_name in college_names
    
    # 清理
    db_session.delete(college)
    db_session.commit()


@given(
    college_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    grade_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
)
def test_grade_creation_with_college_relationship(db_session: Session, college_name: str, grade_name: str):
    """
    **Feature: class-file-collection, Property 1: 组织结构创建一致性**
    对于任意年级名称，创建后该实体应出现在对应学院下，且关联关系正确。
    """
    # 创建学院
    college = College(name=college_name)
    db_session.add(college)
    db_session.commit()
    db_session.refresh(college)
    
    # 创建年级
    grade = Grade(name=grade_name, college_id=college.id)
    db_session.add(grade)
    db_session.commit()
    db_session.refresh(grade)
    
    # 验证年级存在且关联正确
    grades = db_session.query(Grade).filter(Grade.college_id == college.id).all()
    grade_names = [g.name for g in grades]
    assert grade_name in grade_names
    assert grade.college_id == college.id
    
    # 清理
    db_session.delete(college)
    db_session.commit()


@given(
    college_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    grade_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    class_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
)
def test_class_creation_with_grade_relationship(db_session: Session, college_name: str, grade_name: str, class_name: str):
    """
    **Feature: class-file-collection, Property 1: 组织结构创建一致性**
    对于任意班级名称，创建后该实体应出现在对应年级下，且关联关系正确。
    """
    # 创建学院
    college = College(name=college_name)
    db_session.add(college)
    db_session.commit()
    
    # 创建年级
    grade = Grade(name=grade_name, college_id=college.id)
    db_session.add(grade)
    db_session.commit()
    
    # 创建班级
    class_ = Class(name=class_name, grade_id=grade.id)
    db_session.add(class_)
    db_session.commit()
    db_session.refresh(class_)
    
    # 验证班级存在且关联正确
    classes = db_session.query(Class).filter(Class.grade_id == grade.id).all()
    class_names = [c.name for c in classes]
    assert class_name in class_names
    assert class_.grade_id == grade.id
    
    # 清理
    db_session.delete(college)
    db_session.commit()


# ============ Property 3: 级联删除一致性 ============
# **Feature: class-file-collection, Property 3: 级联删除一致性**
# **Validates: Requirements 1.5, 1.6, 1.7**

@given(
    college_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    grade_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    class_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
)
def test_cascade_delete_college(db_session: Session, college_name: str, grade_name: str, class_name: str):
    """
    **Feature: class-file-collection, Property 3: 级联删除一致性**
    删除学院应同时删除其下所有年级和班级。
    """
    # 创建完整的组织结构
    college = College(name=college_name)
    db_session.add(college)
    db_session.commit()
    
    grade = Grade(name=grade_name, college_id=college.id)
    db_session.add(grade)
    db_session.commit()
    
    class_ = Class(name=class_name, grade_id=grade.id)
    db_session.add(class_)
    db_session.commit()
    
    grade_id = grade.id
    class_id = class_.id
    
    # 删除学院
    db_session.delete(college)
    db_session.commit()
    
    # 验证年级和班级也被删除
    assert db_session.query(Grade).filter(Grade.id == grade_id).first() is None
    assert db_session.query(Class).filter(Class.id == class_id).first() is None


@given(
    college_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    grade_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    class_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
)
def test_cascade_delete_grade(db_session: Session, college_name: str, grade_name: str, class_name: str):
    """
    **Feature: class-file-collection, Property 3: 级联删除一致性**
    删除年级应同时删除其下所有班级。
    """
    # 创建组织结构
    college = College(name=college_name)
    db_session.add(college)
    db_session.commit()
    
    grade = Grade(name=grade_name, college_id=college.id)
    db_session.add(grade)
    db_session.commit()
    
    class_ = Class(name=class_name, grade_id=grade.id)
    db_session.add(class_)
    db_session.commit()
    
    class_id = class_.id
    
    # 删除年级
    db_session.delete(grade)
    db_session.commit()
    
    # 验证班级也被删除，但学院保留
    assert db_session.query(Class).filter(Class.id == class_id).first() is None
    assert db_session.query(College).filter(College.id == college.id).first() is not None
    
    # 清理
    db_session.delete(college)
    db_session.commit()


# ============ Property 5: 成员CRUD操作一致性 ============
# **Feature: class-file-collection, Property 5: 成员CRUD操作一致性**
# **Validates: Requirements 2.4, 2.5, 2.6**

@given(
    student_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    gender=st.sampled_from(['男', '女']),
    dormitory=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
)
def test_member_crud_consistency(db_session: Session, student_id: str, name: str, gender: str, dormitory: str):
    """
    **Feature: class-file-collection, Property 5: 成员CRUD操作一致性**
    对于任意成员信息，创建后应能查询到该成员；更新后应反映新值；删除后应无法查询到。
    """
    # 先创建班级
    college = College(name="测试学院")
    db_session.add(college)
    db_session.commit()
    
    grade = Grade(name="测试年级", college_id=college.id)
    db_session.add(grade)
    db_session.commit()
    
    class_ = Class(name="测试班级", grade_id=grade.id)
    db_session.add(class_)
    db_session.commit()
    
    # 创建成员
    member = Member(
        student_id=student_id,
        name=name,
        gender=gender,
        dormitory=dormitory,
        class_id=class_.id
    )
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)
    
    # 验证创建 - 能查询到
    found = db_session.query(Member).filter(Member.student_id == student_id).first()
    assert found is not None
    assert found.name == name
    assert found.gender == gender
    assert found.dormitory == dormitory
    
    # 验证更新
    new_name = name + "_updated"
    found.name = new_name
    db_session.commit()
    db_session.refresh(found)
    assert found.name == new_name
    
    # 验证删除
    member_id = found.id
    db_session.delete(found)
    db_session.commit()
    assert db_session.query(Member).filter(Member.id == member_id).first() is None
    
    # 清理
    db_session.delete(college)
    db_session.commit()
