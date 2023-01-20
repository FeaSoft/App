! Description:
! Definition of a section.
module m_section
    implicit none
    
    private
    public t_section, new_section, CPS, CPE, C3D, ERROR_UNDEFINED_SECTION_TYPE
    
    ! available section types
    integer, parameter :: CPS = 101, & ! 2D continuum (solid) plane stress
                          CPE = 102, & ! 2D continuum (solid) plane strain
                          C3D = 103    ! 3D continuum (solid) general
    
    ! error messages
    character(*), parameter :: ERROR_UNDEFINED_SECTION_TYPE = 'ERROR: Undefined section type.'
    
    type t_section
        integer :: t_section  ! type of section
        integer :: i_eset     ! index of element set
        integer :: i_material ! index o material
        real    :: thickness  ! plane thickness
    end type
    
    interface new_section
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Section constructor.
    type(t_section) function constructor(t_section, i_eset, i_material, thickness) result(this)
        integer, intent(in) :: t_section  ! type of section
        integer, intent(in) :: i_eset     ! index of element set
        integer, intent(in) :: i_material ! index o material
        real,    intent(in) :: thickness  ! plane thickness
        this%t_section  = t_section
        this%i_eset     = i_eset
        this%i_material = i_material
        this%thickness  = thickness
    end function
    
end module
