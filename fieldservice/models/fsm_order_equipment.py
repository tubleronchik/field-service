from odoo import models, fields, tools, api


class FsmOrderWithEquipment(models.Model):
    _name = 'fsm.order.with.equipment'
    _description = 'FSM Order with Equipment'

    order_id = fields.Many2one('fsm.order', string='Order', required=True)
    equipment_id = fields.Many2one('fsm.equipment', string='Equipment', required=True)
    order_name = fields.Char(related='order_id.name', string="Order name", store=True)
    equipment_name = fields.Char(related='equipment_id.name', string='Equipment Name', store=True)
    quantity_available = fields.Integer(related='equipment_id.quantity_available', string='Quantity Available', store=True)
    quantity_used = fields.Integer(string='Quantity Used', default=0, store=True)
    quantity_used_old = fields.Integer(string="Service variable", store=True)

    # Add table definition to create table and columns
    _auto = False

    def init(self):
        # tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f'DROP TABLE IF EXISTS {self._table} CASCADE')
        self.env.cr.execute(
            """
            CREATE TABLE IF NOT EXISTS fsm_order_with_equipment (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES fsm_order(id) ON DELETE CASCADE,
                equipment_id INTEGER REFERENCES fsm_equipment(id) ON DELETE CASCADE,
                quantity_used INTEGER,
                quantity_used_old INTEGER,
                equipment_name VARCHAR,
                quantity_available INTEGER,
                order_name VARCHAR,
                CONSTRAINT unique_order_equipment UNIQUE (order_id, equipment_id)
            )
            """
        )
        self.env.cr.execute(
        """
            INSERT INTO fsm_order_with_equipment (order_id, equipment_id, quantity_used, equipment_name, quantity_available, order_name, quantity_used_old)
            SELECT
            T1.order_id "order_id",
            T1.equipment_id "equipment_id", 
            0 "quantity_used",
            T1.equipment_name "equipment_name",
            T1.quantity_available "quantity_available",
            T1.order_name "order_name",
            0 "quantity_used_old"
            FROM
                (
                    SELECT 
                        fsm_equipment.id "equipment_id", 
                        fsm_equipment.name "equipment_name",
                        fsm_equipment.quantity_available "quantity_available",
                        fsm_equipment_fsm_order_rel.fsm_order_id "order_id",
                        fsm_order.name "order_name"
                    FROM 
                        fsm_equipment
                    LEFT JOIN fsm_equipment_fsm_order_rel on fsm_equipment.id=fsm_equipment_fsm_order_rel.fsm_equipment_id
                    LEFT JOIN fsm_order on fsm_equipment_fsm_order_rel.fsm_order_id=fsm_order.id
                )T1
        """
        )
    # Commit changes to the database
        self.env.cr.commit()

    @api.model
    def create(self, vals):
        res = super().create(vals)
         # update recrods
        if 'quantity_used' in vals: 
            for updated_record in res:
                updated_record.equipment_id.quantity_used_old = 0
                updated_record.equipment_id.quantity_used = updated_record.quantity_used
        return res

    def write(self, vals):
        if 'quantity_used' in vals:
            for outdated_record in self: # save the old quantity_used if the value is updating
                old_quantity_used = outdated_record.quantity_used
                vals['quantity_used_old'] = old_quantity_used
        res = super().write(vals) # update records
        if 'quantity_used' in vals: 
            for updated_record in self:
                updated_record.equipment_id.quantity_used_old = old_quantity_used
                updated_record.equipment_id.quantity_used = updated_record.quantity_used
        return res
