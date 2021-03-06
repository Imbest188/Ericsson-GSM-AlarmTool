from sqlalchemy import MetaData, Table, String, Integer, Column, Boolean, DateTime
from sqlalchemy import create_engine, insert, update, delete, select, exc

from ..Telnet.Alarm import Alarm


class AlarmDatabase:
    def __init__(self):
        self.engine = create_engine('sqlite:///alarms.db')
        self.create_alarm_table()
        self.clear_tables()

    def clear_tables(self):
        conn = self.engine.connect()
        conn.execute(delete(self.alarms))
        conn.execute(delete(self.nodes))

    def create_alarm_table(self):
        metadata = MetaData()
        self.alarms = Table('alarmwindow_alarms', metadata,
                            Column('id', Integer(), nullable=False),
                            Column('type', String(7), nullable=False),
                            Column('raising_time', DateTime, nullable=False),
                            Column('ceasing_time', DateTime, nullable=True),
                            Column('managed_object', String(30)),
                            Column('object_name', String(30)),
                            Column('slogan', String(30)),
                            Column('descr', String(60)),
                            Column('text', String(300), nullable=False),
                            Column('is_active', Boolean(), nullable=False),
                            Column('node_id', Integer()),
                            Column('node_update_id', Integer())
                            )

        self.nodes = Table('alarmwindow_nodes', metadata,
                           Column('id', Integer(), autoincrement=True, primary_key=True),
                           Column('name', String(20), nullable=False, unique=True),
                           Column('update_id', Integer(), default=0)
                           )
        metadata.create_all(self.engine)

    def get_current_update_id(self, node_id) -> int:
        conn = self.engine.connect()
        query = select(self.nodes.c.update_id).where(
            self.nodes.c.id == node_id
        )
        result = conn.execute(query).fetchone()
        return result[0]

    def insert_new_alarms(self, alarm_objects: list[Alarm]):
        if not len(alarm_objects):
            return
        target_node = None
        update_id = self.get_current_update_id(alarm_objects[0].node_id)
        query = insert(self.alarms).values(
            [
                {
                    'id': alarm.id,
                    'type': alarm.type,
                    'raising_time': alarm.raising_time,
                    'managed_object': alarm.managed_object,
                    'object_name': alarm.object_name,
                    'slogan': alarm.slogan,
                    'descr': alarm.descr,
                    'text': alarm.text,
                    'is_active': alarm.is_active,
                    'node_id': alarm.node_id,
                    'node_update_id': update_id if alarm.node_id == target_node
                    else self.get_current_update_id(alarm.node_id)
                } for alarm in alarm_objects
            ]
        )

        conn = self.engine.connect()
        conn.execute(query)

    def update_ceased_alarms(self, alarm_objects: list[Alarm]):
        if not len(alarm_objects):
            return
        conn = self.engine.connect()
        transaction = conn.begin()
        last_node = None
        update_id = self.get_current_update_id(alarm_objects[0].node_id)
        for alarm in alarm_objects:
            if last_node != alarm.node_id:
                update_id = self.get_current_update_id(alarm.node_id)
                last_node = alarm.node_id
            upd = update(self.alarms).where(
                self.alarms.c.id == alarm.id
            ).values({
                'is_active': False,
                'ceasing_time': alarm.ceasing_time,
                'node_update_id': update_id
            })
            conn.execute(upd)
        transaction.commit()

    def increase_update_id(self, controller_id):
        conn = self.engine.connect()
        upd = update(self.nodes).where(
            self.nodes.c.id == controller_id
        ).values(
            {'update_id': self.nodes.c.update_id + 1}
        )
        conn.execute(upd)

    def add_node(self, node_name):
        conn = self.engine.connect()
        query = insert(self.nodes).values(
            {
                'name': node_name,
                'update_id': 0
            }
        )
        try:
            conn.execute(query)
        except exc.IntegrityError:
            pass

    def get_node_id(self, name) -> int:
        conn = self.engine.connect()
        query = select(self.nodes.c.id).where(
            self.nodes.c.name == name
        )
        result = conn.execute(query).fetchone()
        return result[0]
