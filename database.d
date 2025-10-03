CREATE DATABASE PLATINUM2;
USE PLATINUM2;

CREATE TABLE colaborador(
	nome_colaborador varchar(255) not null primary key,
    cpf varchar(15) unique not null,
	telefone bigint not null,
    email varchar (255),
    endereço varchar(255)
);
drop table colaborador;


CREATE TABLE cliente(
	nome_cliente varchar(255) not null primary key,
    placa varchar(255) not null,
	cpf varchar(15)  unique not null,
    telefone bigint not null,
	endereço varchar (255) not null,
    email varchar (255)
);

alter table cliente change placa placa varchar(255);


CREATE TABLE carro(
	placa varchar(255) not null primary key ,
    nome_cliente varchar(255),
    marca_modelo varchar(255) not null,
    FOREIGN KEY (nome_cliente) REFERENCES cliente(nome_cliente)
);

DROP TABLE cliente;
DROP TABLE serviços;


CREATE TABLE fornecedor(
	nome_fornecedor varchar(255) not null primary key,
	endereço varchar(255) not null,
    produto varchar(255),
	CNPJ bigint not null,
	telefone bigint not null
);
DROP TABLE fornecedor;

CREATE TABLE lista_compras (
    nome_peca         VARCHAR(255)    NOT NULL PRIMARY KEY,
    nome_fornecedor   VARCHAR(255)    NOT NULL,
    valor_unit        DECIMAL(10,2)   NOT NULL,
    valor_total       DECIMAL(10,2)   NOT NULL,
    quantidade        INT             NOT NULL,
    FOREIGN KEY (nome_fornecedor) REFERENCES fornecedor(nome_fornecedor)
);

CREATE TABLE estoque (
    nome_peca       VARCHAR(255)    NOT NULL,
    nome_fornecedor VARCHAR(255)    NOT NULL,
    quantidade      INT             NOT NULL,
    valor_unit      DECIMAL(10,2)   NOT NULL,
    valor_total     DECIMAL(10,2)   NOT NULL,
    FOREIGN KEY (nome_fornecedor) REFERENCES fornecedor(nome_fornecedor)
);

drop table estoque;

CREATE TABLE compromissos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    data_compromisso DATE NOT NULL,
    tipo VARCHAR(255),
    descricao VARCHAR(255) NOT NULL
);         
DROP TABLE compromissos;


CREATE TABLE serviços (
    id_serviço INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome_cliente varchar (255),
    placa varchar(255) NOT NULL, 
    valor_total DECIMAL(10, 2) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    forma_pagamento VARCHAR(50) NOT NULL,
    FOREIGN KEY (nome_cliente) REFERENCES cliente(nome_cliente),
	FOREIGN KEY (placa) REFERENCES carro(placa) -- Referência para a tabela 'carro'
);

drop table serviços;

-- Inserir dados na tabela 'colaborador'
INSERT INTO colaborador (nome_colaborador, cpf, telefone, email, endereço) VALUES
('João da Silva', '123.456.789-00', 47999214018, 'joao.silva@example.com', 'Rua dos Mecânicos, 45, São Paulo - SP'),
('Ana Costa', '987.654.321-00', 47999214019, 'ana.costa@example.com', 'Av. Paulista, 1000, São Paulo - SP');

/*-- Inserir dados na tabela 'carro'
INSERT INTO carro (placa) VALUES
('ABC-1234', 'Volkswagen Gol' ),
('XYZ-5678', 'Carlos Oliveira', 'Fiat Punto'),
('JKL-9101', 'Fernanda Lima', 'Chevrolet Onix'),
('LMN-1122', 'Roberto Silva', 'Toyota Corolla');

-- Inserir dados na tabela 'cliente'
INSERT INTO cliente(nome_cliente, cpf, telefone, endereço, email) VALUES
('Maria Souza', 'ABC-1234','123.456.789-01', 11912345678, 'Rua das Flores, 123, Bairro Primavera, São Paulo - SP', 'maria@yahool.com'),
('Carlos Oliveira', 'XYZ-5678', '987.654.321-01', 11987654321, 'Rua dos Pássaros, 321, Jardim Planalto, São Paulo - SP', 'carlos@gmail.com'),
('Fernanda Lima', 'JKL-9101', '321.654.987-02', 11923456789, 'Avenida Brasil, 456, Centro, São Paulo - SP', 'fer_lima@hotmail'),
('Roberto Silva', 'LMN-1122', '456.789.123-03', 11934567890, 'Rua dos Jacarandás, 789, Bairro Nova Vida, São Paulo - SP', 'R.Silva@gmail.com');*/

-- Inserir dados na tabela 'fornecedor'
INSERT INTO fornecedor (nome_fornecedor, endereço, produto, CNPJ, telefone) VALUES
('Auto Peças Ltda', 'Rua das Ferramentas, 123, São Paulo - SP', 'Peças de Carro', 12345678000123, 1122334455),
('Peças Rápidas', 'Av. dos Mecânicos, 500, São Paulo - SP', 'Óleos e Filtros', 98765432000198, 1198765432),
('Ferragens & Cia', 'Rua dos Metalúrgicos, 300, São Paulo - SP', 'Ferragens Automotivas', 11122333445566, 1133445566);

-- Inserir dados na tabela 'lista_compras'
INSERT INTO lista_compras (nome_peca, nome_fornecedor, valor_unit, valor_total, quantidade) VALUES
('Borboleta','Auto Peças Ltda', 100, 500, 5),  
('Calota','Peças Rápidas', 150, 750, 5),  
('Disco de freio','Ferragens & Cia', 200, 1000, 5);

-- Inserir dados na tabela 'compromissos'
INSERT INTO compromissos ( data_compromisso, descricao) VALUES
('2025-03-01', 'Reunião com cliente'),
('2025-03-05', 'Visita técnica no cliente'),
('2025-03-10', 'Entrevista de emprego');

-- Inserir dados na tabela 'serviço'
INSERT INTO serviços ( nome_cliente, placa, valor_total, descricao, forma_pagamento) VALUES
('Maria Souza', 'ABC-1234', 150.00, 'Troca de óleo e filtros', 'Cartão'),
('Carlos Oliveira', 'XYZ-5678', 300.00, 'Reparo de suspensão', 'Dinheiro'),
('Fernanda Lima', 'JKL-9101', 200.00, 'Alinhamento e balanceamento', 'Pix');


select * from colaborador;
select * from cliente;
select * from carro;
select * from fornecedor;
select * from lista_compras;
select * from compromissos;
select * from serviços;
select * from estoque;



INSERT INTO carro (placa, marca_modelo) VALUES
('ABC-1234', 'Volkswagen Gol');
INSERT INTO cliente(nome_cliente,placa, cpf, telefone, endereço, email) VALUES ('Maria Souza', 'ABC-1234','123.456.789-01', 11912345678, 'Rua das Flores, 123, Bairro Primavera, São Paulo - SP', 'maria@yahool.com');
UPDATE carro set nome_cliente = 'Maria Souza' WHERE placa = 'ABC-1234';


alter table cliente add constraint fk foreign key (placa) references carro(placa);

ALTER TABLE cliente DROP FOREIGN KEY fk;