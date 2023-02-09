! Description:
! Definition of a section.
module m_section
    implicit none
    
    private
    public t_section, new_section, CPS, CPE, C3D, ERROR_UNDEFINED_SECTION_TYPE
    
    ! available section types
    integer, parameter :: CPS = 101, & ! 2D continuum (solid) plane stress
                          CPE = 102, & ! 2D continuum (solid) plane strain
                          C3D = 103    ! 3D continuum (solid) general case
    
    ! error messages
    character(*), parameter :: ERROR_UNDEFINED_SECTION_TYPE = 'Error: undefined section type'
    
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
    type(t_section) function constructor(m_space, t_section, i_eset, i_material, thickness) result(self)
        integer, intent(in) :: m_space    ! modeling space
        integer, intent(in) :: t_section  ! type of section
        integer, intent(in) :: i_eset     ! index of element set
        integer, intent(in) :: i_material ! index o material
        real,    intent(in) :: thickness  ! plane thickness
        self%t_section  = t_section
        self%i_eset     = i_eset
        self%i_material = i_material
        if (m_space == 2) then
            self%thickness = thickness
        else
            self%thickness = 1.0
        end if
    end function
    
end module
