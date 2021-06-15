from sqlalchemy     import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Time, CheckConstraint, Index
from sqlalchemy.orm import relationship

from ...db_config    import Base
from .overlord      import Human


class Teacher(Base):
    __tablename__ = 'teacher'
    _name = 'Teacher'

    id                  = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    teacher_global_id   = Column(String(120), nullable=True)
    human_id            = Column(Integer, ForeignKey('overlord.human.id', ondelete='CASCADE'))

    __table_args__ = (
        Index('indx_teacher_tgi', teacher_global_id, unique=True, postgresql_where=teacher_global_id.is_not(None))
        , {'schema' : 'parquet'}
    )

    human       = relationship('Human', back_populates='teacher')


class Student(Base):
    __tablename__ = 'student'
    _name = 'Student'

    id                  = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    student_global_id   = Column(String(120), nullable=True) #!! with index on not null
    human_id            = Column(Integer, ForeignKey('overlord.human.id', ondelete='CASCADE'))
    group_id            = Column(Integer, ForeignKey('parquet.group.id', ondelete='CASCADE'))

    __table_args__ = (
        Index('indx_student_sgi', student_global_id, unique=True, postgresql_where=student_global_id.is_not(None))
        , {'schema' : 'parquet'}
    )

    human                   = relationship('Human', back_populates='student')
    group                   = relationship('Group', back_populates='students')
    student_class_records   = relationship('StudentClassRecord', back_populates='student')


class Group(Base):
    __tablename__ = 'group'
    _name = 'Group'

    id                  = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    group_global_id     = Column(String(120), nullable=True)
    name                = Column(String(20), nullable=False)
    study_start_dt      = Column(DateTime)
    study_end_dt        = Column(DateTime)

    __table_args__ = (
        Index('indx_group_ggi', group_global_id, unique=True, postgresql_where=group_global_id.is_not(None))
        , {'schema' : 'parquet'}
    )

    students            = relationship('Student', back_populates='group')


class ClassTime(Base): # TODO!
    __table_args__ = {'schema' : 'parquet'}
    __tablename__ = 'class_times'
    _name = 'ClassTime'

    class_no            = Column(Integer, nullable=False, primary_key=True, unique=True)
    start_time          = Column(Time(timezone=False))
    end_time            = Column(Time(timezone=False))
    break_start_time    = Column(Time(timezone=False))
    break_end_time      = Column(Time(timezone=False))


class Class(Base):
    __tablename__ = 'class'
    _name = 'Class'

    id              = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    class_global_id = Column(String(120), nullable=True)
    name            = Column(String(50))

    __table_args__ = (
        Index('indx_class_cgi', class_global_id, unique=True, postgresql_where=class_global_id.is_not(None))
        , {'schema' : 'parquet'}
    )


class DayOfWeek(Base):
    __table_args__ = {'schema' : 'parquet'}
    __tablename__ = 'days_of_week'
    _name = 'DayOfWeek'

    day_no          = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name            = Column(String(16), nullable=False)
    short_name      = Column(String(5), nullable=False)
    #! ml_id  = Dependent on external sequence # multilanguage id for localization
    # ML_Table (id, language, translated_text, original_table_id) -- id and language are primary key here
    # tables(id, table_name)


class ScheduledClass(Base):
    __table_args__ = {'schema' : 'parquet'}
    __tablename__ = 'scheduled_class'
    _name = 'ScheduledClass'

    id                  = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    teacher_id          = Column(Integer, ForeignKey('overlord.human.id', ondelete='SET NULL'))
    group_id            = Column(Integer, ForeignKey('parquet.group.id', ondelete='SET NULL'))
    class_id            = Column(Integer, ForeignKey('parquet.class.id', ondelete='CASCADE'))
    week_no             = Column(Integer) # TODO: check(week < 2)
    day                 = Column(Integer) #* foreign key days DayOfWeek
    class_no            = Column(Integer) # TODO: class num refers to table of class num and respective time of class begin and end (ClassTime)

    class_instances     = relationship('ClassInstance', back_populates='scheduled_class')


class TypeOfAssignment(Base):
    __table_args__ = {'schema' : 'parquet'}
    __tablename__ = 'type_of_assignment'
    _name = 'TypeOfAssignment'

    id      = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name    = Column(String(50))


class ClassInstance(Base):
    __tablename__ = 'class_instance'
    _name = 'ClassInstance'
    __table_args__ = (
        CheckConstraint('scheduled_class_id is null or ( group_id is null and class_id is null and teacher_id is null)')
        , {'schema' : 'parquet'}
    )

    id                          = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    class_dt                    = Column(DateTime, nullable=False)
    teacher_id                  = Column(Integer, ForeignKey('parquet.teacher.id', ondelete='SET NULL'), nullable=True)
    group_id                    = Column(Integer, ForeignKey('parquet.group.id', ondelete='SET NULL'), nullable=True)
    class_id                    = Column(Integer, ForeignKey('parquet.class.id', ondelete='SET NULL'), nullable=True)
    scheduled_class_id          = Column(Integer, ForeignKey('parquet.scheduled_class.id', ondelete='SET NULL'), nullable=True) #* if it is present it means class was scheduled normally
    allow_change_by_non_teacher = Column(Boolean, server_default='true')
    # TODO: check constraint scheduled_class_id is null or group_id, class_id are null

    scheduled_class             = relationship('ScheduledClass', back_populates='class_instances')
    student_class_records       = relationship('StudentClassRecord', back_populates='class_instance')


class StudentClassRecord(Base):
    __table_args__ = {'schema' : 'parquet'}
    __tablename__ = 'student_class_record'
    _name = 'StudentClassRecord'

    id                          = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    class_instance_id           = Column(Integer, ForeignKey('parquet.class_instance.id', ondelete='CASCADE'), nullable=True)
    type_of_assignment_id       = Column(Integer, ForeignKey('parquet.type_of_assignment.id', ondelete='SET NULL'), nullable=True)
    student_id                  = Column(Integer, ForeignKey('parquet.student.id', ondelete='SET NULL'), nullable=True)
    mark                        = Column(Integer) # TODO: check(0 <= mark <= 100) and change to float
    comment                     = Column(Text)
    is_present                  = Column(Boolean)

    class_instance             = relationship('ClassInstance', back_populates='student_class_records')
    type_of_assignment         = relationship('TypeOfAssignment')
    student                    = relationship('Student', back_populates='student_class_records')
