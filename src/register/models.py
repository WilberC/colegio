"""
Modelos relacionados a los registros de las diferentes entidades

Autor: Raul Talledo <raul.talledo@technancial.com.pe>

Fecha: 23/07/2017

"""
from django.db import models

from utils.misc import insert_child
from utils.models import CreacionModificacionUserMixin, CreacionModificacionFechaPersonalMixin, \
    CreacionModificacionFechaApoderadoMixin, CreacionModificacionFechaAlumnoMixin, \
    CreacionModificacionFechaPromotorMixin, CreacionModificacionFechaCajeroMixin, \
    CreacionModificacionFechaDirectorMixin, \
    CreacionModificacionUserPersonalMixin, CreacionModificacionUserApoderadoMixin, \
    CreacionModificacionUserAlumnoMixin, \
    CreacionModificacionUserPromotorMixin, CreacionModificacionUserCajeroMixin, CreacionModificacionUserDirectorMixin
from utils.models import CreacionModificacionFechaMixin
from utils.models import ActivoMixin

from profiles.models import Profile


class Personal(CreacionModificacionUserPersonalMixin, CreacionModificacionFechaPersonalMixin, Profile, models.Model):
    """
    Clase para el Personal
    """
    id_personal = models.AutoField(primary_key=True)
    persona = models.OneToOneField(Profile, models.DO_NOTHING, parent_link=True)
    activo_personal = models.BooleanField(db_column="activo", default=True)

    @staticmethod
    def savePersonalFromPersona(persona: Profile, **atributos):
        return insert_child(persona, Personal, **atributos)

    class Meta:
        managed = False
        db_table = 'personal'


class Colegio(ActivoMixin, CreacionModificacionFechaMixin, CreacionModificacionUserMixin, models.Model):
    """
    Clase para el Colegio
    """
    id_colegio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=11)
    ugel = models.CharField(max_length=100)
    personales = models.ManyToManyField(Personal, through='PersonalColegio', related_name='Colegios', null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        db_table = 'colegio'


class Telefono(ActivoMixin, CreacionModificacionUserMixin, CreacionModificacionFechaMixin, models.Model):
    """
    Clase que guarda toda la información relacionada a los teléfonos que pueden estar vinculado a model: #Personas
    o #Colegio
    """
    id_telefono = models.AutoField(primary_key=True)
    colegio = models.ForeignKey(Colegio, models.DO_NOTHING, db_column='id_colegio', related_name="telefonos")
    persona = models.ForeignKey(Profile, models.DO_NOTHING, db_column='id_persona', related_name="telefonos")
    numero = models.IntegerField()
    tipo = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'telefono'


class Direccion(CreacionModificacionUserMixin, CreacionModificacionFechaMixin, models.Model):
    """
    Clase para hacer referencia a las direcciones
    """

    id_direccion = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Profile, models.DO_NOTHING, db_column='id_persona', related_name="direcciones")
    colegio = models.ForeignKey(Colegio, models.DO_NOTHING, db_column='id_colegio', related_name="direcciones")
    calle = models.CharField(max_length=100)
    dpto = models.CharField(max_length=15)
    distrito = models.CharField(max_length=100)
    numero = models.CharField(max_length=6, blank=True, null=True)
    referencia = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'direccion'


class Apoderado(CreacionModificacionUserApoderadoMixin, CreacionModificacionFechaApoderadoMixin, Profile, models.Model):
    """
    Clase para identificar a los apoderados de los alumnos
    """
    id_apoderado = models.AutoField(primary_key=True)
    parentesco = models.CharField(max_length=30)
    persona = models.OneToOneField(Profile, models.DO_NOTHING, parent_link=True, )

    @staticmethod
    def saveApoderadoFromPersona(persona: Profile, **atributos):
        """
        Método que permite guardar un Apoderado a partir de una persona existente
        :param persona: Persona existente
        :param atributos: Nuevos atributos propios de Apoderado
        :return: Objeto Apoderado creado
        """
        return insert_child(persona, Apoderado, **atributos)

    class Meta:
        managed = False
        db_table = 'apoderado'


class Alumno(CreacionModificacionUserAlumnoMixin, CreacionModificacionFechaAlumnoMixin, Profile, models.Model):
    """
    Clase para identificar a los Alumnos
    """
    id_alumno = models.AutoField(primary_key=True)
    codigoint = models.CharField(max_length=15, blank=True, null=True)
    persona = models.OneToOneField(Profile, models.DO_NOTHING, parent_link=True)
    apoderados = models.ManyToManyField(Apoderado, through='ApoderadoAlumno', related_name='alumnos', null=True)

    @staticmethod
    def saveAlumnoFromPersona(persona: Profile, **atributos):
        """
        Método que permite guardar un Apoderado a partir de una persona existente
        :param persona: Persona existente
        :param atributos: Nuevos atributos propios de Apoderado
        :return: Objeto Alumno creado
        """
        return insert_child(persona, Alumno, **atributos)

    class Meta:
        managed = False
        db_table = 'alumno'


class ApoderadoAlumno(ActivoMixin, CreacionModificacionFechaMixin, CreacionModificacionUserMixin, models.Model):
    """
    Clase para relacionar los Apoderado de los Alumnos
    """
    id_apoderadoalumno = models.AutoField(primary_key=True)
    apoderado = models.ForeignKey(Apoderado, models.DO_NOTHING, db_column='id_apoderado')
    alumno = models.ForeignKey(Alumno, models.DO_NOTHING, db_column='id_alumno')

    class Meta:
        managed = False
        db_table = 'apoderado_alumno'
        unique_together = (("apoderado", "alumno"),)


class Promotor(CreacionModificacionUserPromotorMixin, CreacionModificacionFechaPromotorMixin, Personal, models.Model):
    """
    Clase para el Promotor
    """
    id_promotor = models.AutoField(primary_key=True)
    personalprom = models.OneToOneField(Personal, models.DO_NOTHING, parent_link=True, )
    activo_promotor = models.BooleanField(default=True, db_column="activo")

    @staticmethod
    def savePromotorFromPersonal(personal: Personal, **atributos):
        """
        # Método que permite guardar un Promotor a partir de un personal existente
        # :param personal: Personal existente
        # :param atributos: Nuevos atributos propios de Apoderado
        # :return: Objeto Promotor creado
        """

        return insert_child(personal, Promotor, **atributos)

    class Meta:
        managed = False
        db_table = 'promotor'


class Cajero(CreacionModificacionUserCajeroMixin, CreacionModificacionFechaCajeroMixin, Personal, models.Model):
    """
    Clase para el Cajero
    """
    id_cajero = models.AutoField(primary_key=True)
    personalcajero = models.OneToOneField(Personal, models.DO_NOTHING, parent_link=True, )
    activo_cajero = models.BooleanField(default=True, db_column="activo")

    @staticmethod
    def saveCajeroFromPersonal(personal: Personal, **atributos):
        """
        # Método que permite guardar un Promotor a partir de un personal existente
        # :param personal: Personal existente
        # :param atributos: Nuevos atributos propios de Apoderado
        # :return: Objeto Promotor creado
        """

        return insert_child(personal, Cajero, **atributos)

    class Meta:
        managed = False
        db_table = 'cajero'


class Director(CreacionModificacionUserDirectorMixin, CreacionModificacionFechaDirectorMixin, Personal, models.Model):
    """
    Clase para el Director
    """
    id_director = models.AutoField(primary_key=True)
    personaldirector = models.OneToOneField(Personal, models.DO_NOTHING, parent_link=True, )
    activo_director = models.BooleanField(default=True, db_column="activo")

    @staticmethod
    def saveDirectorFromPersonal(personal: Personal, **atributos):
        """
        # Método que permite guardar un Promotor a partir de un personal existente
        # :param personal: Personal existente
        # :param atributos: Nuevos atributos propios de Apoderado
        # :return: Objeto Promotor creado
        """

        return insert_child(personal, Director, **atributos)

    class Meta:
        managed = False
        db_table = 'director'


class PersonalColegio(ActivoMixin, CreacionModificacionUserMixin, CreacionModificacionFechaMixin, models.Model):
    """
    Clase que relacion el Personal con un Colegio
    """
    id_personal_colegio = models.AutoField(primary_key=True)
    personal = models.ForeignKey(Personal, models.DO_NOTHING, db_column="id_personal")
    colegio = models.ForeignKey(Colegio, models.DO_NOTHING, db_column="id_colegio")

    class Meta:
        managed = False
        db_table = 'personal_colegio'
