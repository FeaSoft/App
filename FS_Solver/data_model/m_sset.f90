! Description:
! Definition of a surface set.
module m_sset
    use m_surface
    implicit none
    
    private
    public t_sset, new_sset
    
    type t_sset
        integer                      :: n_surfaces  ! number of surfaces
        type(t_surface), allocatable :: surfaces(:) ! surfaces
    contains
        final :: destructor
    end type
    
    interface new_sset
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Surface set constructor.
    type(t_sset) function constructor(n_surfaces) result(self)
        integer, intent(in) :: n_surfaces ! number of surfaces
        self%n_surfaces = n_surfaces
        allocate(self%surfaces(self%n_surfaces))
    end function
    
    ! Description:
    ! Surface set destructor.
    subroutine destructor(self)
        type(t_sset), intent(inout) :: self
        if (allocated(self%surfaces)) deallocate(self%surfaces)
    end subroutine
    
end module
