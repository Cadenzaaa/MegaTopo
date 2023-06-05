/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2022/12/6 13:05:40                           */
/*==============================================================*/


drop table if exists Alias;

drop table if exists Geolocation;

drop table if exists Node;

drop table if exists Operation;

drop table if exists RTTL;

/*==============================================================*/
/* Table: Alias                                                 */
/*==============================================================*/
create table Alias
(
   addr1                char(46) not null,
   addr2                char(46) not null,
   opr_id               int not null,
   primary key (addr1, addr2, opr_id)
);

/*==============================================================*/
/* Table: Geolocation                                           */
/*==============================================================*/
create table Geolocation
(
   node_addr            char(46) not null,
   opr_id               int not null,
   node_lng             float not null,
   node_lat             float not null,
   primary key (node_addr, opr_id)
);

/*==============================================================*/
/* Table: Node                                                  */
/*==============================================================*/
create table Node
(
   node_addr            char(46) not null,
   opr_id               int not null,
   node_ipver           int not null,
   primary key (node_addr)
);

/*==============================================================*/
/* Table: Operation                                             */
/*==============================================================*/
create table Operation
(
   opr_id               int not null auto_increment,
   time                 timestamp not null,
   opr_type             int not null,
   descr                varchar(255),
   primary key (opr_id)
);

/*==============================================================*/
/* Table: RTTL                                                  */
/*==============================================================*/
create table RTTL
(
   node_addr            char(46) not null,
   host_addr            char(46) not null,
   rttl                 int not null,
   opr_id               int not null,
   primary key (node_addr, host_addr, rttl)
);

alter table Alias add constraint FK_Relationship_10 foreign key (opr_id)
      references Operation (opr_id) on delete restrict on update restrict;

alter table Alias add constraint FK_Relationship_8 foreign key (addr2)
      references Node (node_addr) on delete restrict on update restrict;

alter table Alias add constraint FK_Relationship_9 foreign key (addr1)
      references Node (node_addr) on delete restrict on update restrict;

alter table Geolocation add constraint FK_Relationship_4 foreign key (node_addr)
      references Node (node_addr) on delete restrict on update restrict;

alter table Geolocation add constraint FK_Relationship_6 foreign key (opr_id)
      references Operation (opr_id) on delete restrict on update restrict;

alter table Node add constraint FK_Relationship_11 foreign key (opr_id)
      references Operation (opr_id) on delete restrict on update restrict;

alter table RTTL add constraint FK_Relationship_3 foreign key (node_addr)
      references Node (node_addr) on delete restrict on update restrict;

alter table RTTL add constraint FK_Relationship_5 foreign key (opr_id)
      references Operation (opr_id) on delete restrict on update restrict;

